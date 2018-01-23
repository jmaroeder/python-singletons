import logging
import types
from typing import Any, Callable, MutableMapping, Union
from unittest.mock import Mock

from singletons.factory import EventletFactory, GeventFactory, GlobalFactory, GreenthreadFactory, ProcessFactory, \
    ThreadFactory
from singletons.singleton import EventletSingleton, GeventSingleton, GreenthreadSingleton, ProcessSingleton, \
    Singleton, ThreadSingleton
from singletons.utils import env_to_bool


SETUP_MOCK = 'SINGLETONS_SETUP_MOCK'
LOG = logging.getLogger(__name__)


class SharedModule(types.ModuleType):
    """
    Base class used to intercept attribute accesses to a module

    See https://mail.python.org/pipermail/python-ideas/2012-May/014969.html where Guido talks about this technique

    This allows for lazy loading and overriding in the case of ``setup_mock``

    Subclasses must set ``globals`` class attribute.

    Example usage (at the very bottom of a module to be made into a shared module)::

        class _Shared(SharedModule):
            globals = globals()
        sys.modules[__name__] = _Shared()
    """
    _mock: MutableMapping = None

    def __init__(self) -> None:
        if not hasattr(self, 'globals'):
            raise NotImplementedError('SharedModule subclasses must define the `globals` attribute '
                                      '(see documentation for example)')  # pragma: no cover
        self._mock: MutableMapping = None
        if env_to_bool(SETUP_MOCK):
            self.setup_mock()  # pragma: no cover

    def setup_mock(self) -> None:
        """
        Switches the module to ``mock`` mode, or resets all existing Mocks. All attribute accesses will receive mock
        objects instead of actual ones
        """
        self._mock = {}

    def teardown_mock(self) -> None:
        """
        Switches the module out of ``mock`` mode. Removes all existing Mocks.
        """
        self._mock = None

    def _instantiate_mock_instance(self, item: str) -> Union[Callable, Mock]:
        """
        Selects the appropriately scoped mock instance, or a simple Mock
        """
        try:
            original = self.globals[item]
        except KeyError:
            raise AttributeError(f"module '{self.globals['__name__']}' has no attribute '{item}'")

        metaclass = getattr(original, 'singleton_metaclass', None) or type(original)
        if issubclass(metaclass, Singleton):
            factory = GlobalFactory
        elif issubclass(metaclass, ProcessSingleton):
            factory = ProcessFactory
        elif issubclass(metaclass, ThreadSingleton):
            factory = ThreadFactory
        elif issubclass(metaclass, GreenthreadSingleton):
            factory = GreenthreadFactory
        elif issubclass(metaclass, EventletSingleton):
            factory = EventletFactory
        elif issubclass(metaclass, GeventSingleton):
            factory = GeventFactory
        else:
            return Mock()
        LOG.debug('Using factory %s for %s', factory, item)

        # create a factory with the appropriate scope
        @factory
        def _mock_factory():
            return Mock()

        return _mock_factory

    def __getattr__(self, item: str) -> Any:
        if self._mock is None:
            try:
                return self.globals[item]
            except KeyError:
                raise AttributeError(f"module '{self.globals['__name__']}' has no attribute '{item}'")
        if item not in self._mock:
            self._mock[item] = self._instantiate_mock_instance(item)
        return self._mock[item]

    def __setattr__(self, key: str, value: Any) -> None:
        if key == '_mock':
            return super().__setattr__(key, value)
        if self._mock is None:
            self.globals[key] = value
            return
        self._mock[key] = value
