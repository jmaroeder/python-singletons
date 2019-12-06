import os
import threading
from collections import defaultdict
from typing import Any, ClassVar, MutableMapping, Optional, Type, TypeVar

from singletons.utils import greenthread_ident

T = TypeVar("T")  # noqa: WPS111


class Singleton(type):
    """
    Thread-safe singleton metaclass.

    Ensures that one instance is created.

    Note that if the process is forked before any instances have been accessed, then all processes
    will actually each have their own instances. You may be able to avoid this by instantiating the
    instance before forking.

    Usage::

        >>> class Foo(metaclass=Singleton):
        ...     pass
        >>> a = Foo()
        >>> b = Foo()
        >>> assert a is b

    """

    __instances: ClassVar[MutableMapping[Type, Any]] = {}
    __locks: ClassVar[MutableMapping[Type, threading.Lock]] = defaultdict(threading.Lock)

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:  # noqa: D102
        if cls not in Singleton.__instances:
            with Singleton.__locks[cls]:
                if cls not in Singleton.__instances:  # pragma: no branch
                    # double checked locking pattern
                    Singleton.__instances[cls] = super().__call__(*args, **kwargs)  # type: ignore
        return Singleton.__instances[cls]  # type: ignore


class ProcessSingleton(type):
    """
    Thread-safe process-based singleton metaclass.

    Ensures that one instance is created per process.
    """

    __pids: ClassVar[MutableMapping[int, MutableMapping[Type, Any]]] = {}
    __lock = threading.Lock()

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:  # noqa: D102
        pids = ProcessSingleton.__pids
        pid = cls._get_ident()  # type: ignore
        if pid not in pids:
            with ProcessSingleton.__lock:
                if pid not in pids:  # pragma: no branch
                    # double checked locking pattern
                    pids[pid] = {}
                    pids[pid][cls] = super().__call__(*args, **kwargs)  # type: ignore
        my_pid = pids[pid]
        if cls not in my_pid:
            with ProcessSingleton.__lock:
                if cls not in my_pid:  # pragma: no branch
                    # double checked locking pattern
                    my_pid[cls] = super().__call__(*args, **kwargs)  # type: ignore
        return my_pid[cls]  # type: ignore

    @staticmethod
    def _get_ident() -> int:
        """
        Return the identifier for the scope.

        :return: an int unique per process
        """
        return os.getpid()


class ThreadSingleton(type):
    """
    Thread-based singleton metaclass.

    Ensures that one instance is created per thread.
    """

    __local: Optional[threading.local] = None
    __lock = threading.Lock()

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:  # noqa: D102
        cls_id = str(id(cls))
        if ThreadSingleton.__local is None:
            with ThreadSingleton.__lock:
                if ThreadSingleton.__local is None:  # pragma: no branch
                    # double checked locking pattern
                    ThreadSingleton.__local = threading.local()
        if not hasattr(ThreadSingleton.__local, cls_id):
            instance = super().__call__(*args, **kwargs)  # type: ignore
            setattr(ThreadSingleton.__local, cls_id, instance)
        return getattr(ThreadSingleton.__local, cls_id)  # type: ignore


class GreenthreadSingleton(ProcessSingleton):
    """
    Greenthread-based singleton metaclass.

    Ensures that one instance is created per greenthread (either eventlet or gevent is
    autodetected).
    """

    @staticmethod
    def _get_ident() -> int:
        """
        Return the identifier for the greenthread.

        :return: an int unique for the greenthread
        """
        return greenthread_ident()


class EventletSingleton(ProcessSingleton):
    """Greenthread-based singleton metaclass, targeting eventlet specifically."""

    @staticmethod
    def _get_ident() -> int:
        """
        Return the identifier for the greenthread.

        :return: an int unique for the greenthread
        """
        import eventlet.corolocal  # noqa: WPS433

        return eventlet.corolocal.get_ident()


class GeventSingleton(ProcessSingleton):
    """Greenthread-based singleton metaclass, targeting gevent specifically."""

    @staticmethod
    def _get_ident() -> int:
        """
        Return the identifier for the greenthread.

        :return: an int unique for the greenthread
        """
        import gevent.thread  # noqa: WPS433

        return gevent.thread.get_ident()


SINGLETON_TYPES = (
    Singleton,
    ProcessSingleton,
    ThreadSingleton,
    GreenthreadSingleton,
    EventletSingleton,
    GeventSingleton,
)
