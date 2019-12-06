import functools
from typing import Any, Callable

from singletons.singleton import (
    EventletSingleton,
    GeventSingleton,
    GreenthreadSingleton,
    ProcessSingleton,
    Singleton,
    ThreadSingleton,
)


class _FactoryBase:
    """
    Base class for Factory decorators.

    Subclasses must set ``singleton_metaclass`` as a class attribute.
    """

    def __init__(self, func: Callable[[], Any]) -> None:
        if not hasattr(type(self), "singleton_metaclass"):  # noqa: WPS421
            raise NotImplementedError(
                "_FactoryBase subclasses must define the `singleton_metaclass` attribute",
            )  # pragma: no cover

        class _Singleton(metaclass=type(self).singleton_metaclass):  # type: ignore
            """Internal singleton class."""

            def __init__(self) -> None:  # noqa: WPS442
                self.my_obj = func()

        self._singleton_cls = _Singleton
        functools.update_wrapper(self, func)

    def __call__(self) -> Any:
        return self._singleton_cls().my_obj


class GlobalFactory(_FactoryBase):
    """
    Decorator to create a global singleton factory function.

    Example usage::

        @GlobalFactory
        def celery_app():
            app = celery.Celery()
            app.config_from_object('myapp.celeryconfig')
            return app
    """

    singleton_metaclass = Singleton


class ProcessFactory(_FactoryBase):
    """Decorator to create a process singleton factory function."""

    singleton_metaclass = ProcessSingleton


class ThreadFactory(_FactoryBase):
    """Decorator to create a thread singleton factory function."""

    singleton_metaclass = ThreadSingleton


class GreenthreadFactory(_FactoryBase):
    """
    Decorator to create a greenthread singleton factory function.

    Autodetects either eventlet or gevent.
    """

    singleton_metaclass = GreenthreadSingleton


class EventletFactory(_FactoryBase):
    """Decorator to create an eventlet singleton factory function."""

    singleton_metaclass = EventletSingleton


class GeventFactory(_FactoryBase):
    """Decorator to create a gevent singleton factory function."""

    singleton_metaclass = GeventSingleton
