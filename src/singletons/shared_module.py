import logging
import types
from typing import Any, Callable, MutableMapping, Optional, Type, Union
from unittest.mock import Mock

from singletons.factory import (  # noqa: WPS436
    EventletFactory,
    GeventFactory,
    GlobalFactory,
    GreenthreadFactory,
    ProcessFactory,
    ThreadFactory,
    _FactoryBase,
)
from singletons.singleton import (
    EventletSingleton,
    GeventSingleton,
    GreenthreadSingleton,
    ProcessSingleton,
    Singleton,
    ThreadSingleton,
)
from singletons.utils import env_to_bool

SETUP_MOCK = "SINGLETONS_SETUP_MOCK"
LOG = logging.getLogger(__name__)
METACLASS_FACTORY_MAP = types.MappingProxyType(
    {
        Singleton: GlobalFactory,
        ProcessSingleton: ProcessFactory,
        ThreadSingleton: ThreadFactory,
        GreenthreadSingleton: GreenthreadFactory,
        EventletSingleton: EventletFactory,
        GeventSingleton: GeventFactory,
    },
)


class SharedModule(types.ModuleType):
    """
    Base class used to intercept attribute accesses to a module.

    See https://mail.python.org/pipermail/python-ideas/2012-May/014969.html where Guido talks
    about this technique.

    This allows for lazy loading and overriding in the case of ``setup_mock``.

    Subclasses must set ``globals`` class attribute.

    Example usage (at the very bottom of a module to be made into a shared module)::

        class _Shared(SharedModule):
            globals = globals()
        sys.modules[__name__] = _Shared()
    """

    _mock: Optional[MutableMapping] = None

    def __init__(self) -> None:
        if not hasattr(self, "globals"):  # noqa: WPS421
            raise NotImplementedError(
                "SharedModule subclasses must define the `globals` attribute "
                + "(see documentation for example)",
            )  # pragma: no cover
        if env_to_bool(SETUP_MOCK):
            self.setup_mock()  # pragma: no cover

    def setup_mock(self) -> None:
        """
        Switch the module to ``mock`` mode, or reset all existing Mocks.

        All attribute accesses will receive mock objects instead of actual ones.
        """
        self._mock = {}

    def teardown_mock(self) -> None:
        """
        Switch the module out of ``mock`` mode.

        Remove all existing Mocks.
        """
        self._mock = None

    def __getattr__(self, key: str) -> Any:
        if self._mock is None:
            try:
                return self.globals[key]
            except KeyError:
                raise AttributeError(
                    f"module '{self.globals['__name__']}' has no attribute '{key}'",
                )
        if key not in self._mock:
            self._mock[key] = self._instantiate_mock_instance(key)
        return self._mock[key]

    def __setattr__(self, key: str, attr_value: Any) -> None:
        if key == "_mock":
            super().__setattr__(key, attr_value)
        if self._mock is None:
            self.globals[key] = attr_value
            return
        self._mock[key] = attr_value

    def _instantiate_mock_instance(self, key: str) -> Union[Callable, Mock]:
        """
        Select the appropriately scoped mock instance, or a simple Mock.

        :raises: AttributeError
        :arg key: The item name
        :return: The factory or Mock
        """
        try:
            original = self.globals[key]
        except KeyError:
            raise AttributeError(f"module '{self.globals['__name__']}' has no attribute '{key}'")

        metaclass = getattr(original, "singleton_metaclass", None) or type(original)
        factory = self._select_factory(metaclass)
        if factory is None:
            return Mock()
        LOG.debug("Using factory %s for %s", factory, key)

        # create a factory with the appropriate scope
        @factory  # type: ignore
        def _mock_factory() -> Mock:  # noqa: WPS430
            return Mock()

        return _mock_factory

    def _select_factory(self, metaclass: Type) -> Optional[Type[_FactoryBase]]:
        """
        Select the appropriate factory to use based on the metaclass.

        :arg metaclass: One of the Singleton metaclasses
        :return: The appropriate Factory class, or None
        """
        for key, factory in METACLASS_FACTORY_MAP.items():
            if issubclass(metaclass, key):
                return factory
        return None
