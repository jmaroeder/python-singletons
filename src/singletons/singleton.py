"""
Singleton metaclasses, decorators, and helpers
"""
import os
import threading

from singletons.utils import greenthread_ident


class Singleton(type):
    """
    Thread-safe singleton metaclass

    Ensures that one instance is created

    Note that if the process is forked before any instances have been accessed, then all processes will actually
    each have their own instances. You may be able to avoid this by instantiating the instance before forking

    Usage::

        >>> class Foo(metaclass=Singleton):
        ...     pass
        >>> a = Foo()
        >>> b = Foo()
        >>> assert a is b

    """
    __instances = {}
    __lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            with cls.__lock:
                if cls not in cls.__instances:  # pragma: no branch
                    # double checked locking pattern
                    cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


class ProcessSingleton(type):
    """
    Thread-safe process-based singleton metaclass

    Ensures that one instance is created per process
    """
    __pids = {}
    __lock = threading.Lock()

    @staticmethod
    def _get_ident() -> int:
        """
        Returns the identifier for the process
        """
        print('BAM')
        return os.getpid()

    def __call__(cls, *args, **kwargs):
        pid = cls._get_ident()
        if pid not in cls.__pids:
            with cls.__lock:
                if pid not in cls.__pids:  # pragma: no branch
                    # double checked locking pattern
                    cls.__pids[pid] = {}
                    cls.__pids[pid][cls] = super().__call__(*args, **kwargs)
        if cls not in cls.__pids[pid]:
            with cls.__lock:
                if cls not in cls.__pids[pid]:  # pragma: no branch
                    # double checked locking pattern
                    cls.__pids[pid][cls] = super().__call__(*args, **kwargs)
        return cls.__pids[pid][cls]


class ThreadSingleton(type):
    """
    Thread-based singleton metaclass

    Ensures that one instance is created per thread
    """
    _local_func = staticmethod(threading.local)  # should not pass implicit parameter
    __local = None
    __lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        cls_id = str(id(cls))
        if cls.__local is None:
            with cls.__lock:
                if cls.__local is None:  # pragma: no branch
                    # double checked locking pattern
                    cls.__local = cls._local_func()
        try:
            return getattr(cls.__local, cls_id)
        except AttributeError:
            instance = super().__call__(*args, **kwargs)
            setattr(cls.__local, cls_id, instance)
            return instance


class GreenthreadSingleton(ProcessSingleton):
    """
    Greenthread-based singleton metaclass

    Ensures that one instance is created per greenthread (either eventlet or gevent is autodetected)
    """

    @staticmethod
    def _get_ident() -> int:
        return greenthread_ident()


class EventletSingleton(ProcessSingleton):
    """
    Greenthread-based singleton metaclass, targeting eventlet specifically
    """

    @staticmethod
    def _get_ident() -> int:
        import eventlet.corolocal  # pylint: disable=import-error
        return eventlet.corolocal.get_ident()


class GeventSingleton(ProcessSingleton):
    """
    Greenthread-based singleton metaclass, targeting gevent specifically
    """

    @staticmethod
    def _get_ident() -> int:
        import gevent.thread  # pylint: disable=import-error
        return gevent.thread.get_ident()


SINGLETON_TYPES = [Singleton, ProcessSingleton, ThreadSingleton, GreenthreadSingleton, EventletSingleton,
                   GeventSingleton]
