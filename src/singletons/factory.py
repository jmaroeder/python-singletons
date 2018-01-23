"""
Factory decorators
"""
import functools
from typing import Any, Callable

from singletons.singleton import EventletSingleton, GeventSingleton, GreenthreadSingleton, ProcessSingleton, \
    Singleton, ThreadSingleton


class _FactoryBase:
    """
    Base class for Factory decorators

    Subclasses must set ``singleton_metaclass`` as a class attribute
    """

    def __init__(self, f: Callable[[], Any]) -> None:
        if not hasattr(type(self), 'singleton_metaclass'):
            raise NotImplementedError(
                '_FactoryBase subclasses must define the `singleton_metaclass` attribute')  # pragma: no cover

        class _Singleton(metaclass=type(self).singleton_metaclass):  # pylint: disable=undefined-variable
            """
            Internal singleton class
            """

            def __init__(self):
                self.obj = f()

        self._singleton_cls = _Singleton
        functools.update_wrapper(self, f)

    def __call__(self) -> Any:
        return self._singleton_cls().obj


class GlobalFactory(_FactoryBase):
    """
    Decorator to create a global singleton factory function

    Example usage::

        @GlobalFactory
        def celery_app():
            app = celery.Celery()
            app.config_from_object('myapp.celeryconfig')
            return app
    """
    singleton_metaclass = Singleton


class ProcessFactory(_FactoryBase):
    """
    Decorator to create a process singleton factory function
    """
    singleton_metaclass = ProcessSingleton


class ThreadFactory(_FactoryBase):
    """
    Decorator to create a thread singleton factory function
    """
    singleton_metaclass = ThreadSingleton


class GreenthreadFactory(_FactoryBase):
    """
    Decorator to create a greenthread singleton factory function (autodetects either eventlet or gevent)
    """
    singleton_metaclass = GreenthreadSingleton


class EventletFactory(_FactoryBase):
    """
    Decorator to create an eventlet singleton factory function
    """
    singleton_metaclass = EventletSingleton


class GeventFactory(_FactoryBase):
    """
    Decorator to create a gevent singleton factory function
    """
    singleton_metaclass = GeventSingleton
