import multiprocessing
import queue
import threading
from typing import Type
import uuid

import pytest

import singletons
from singletons.exceptions import NoGreenthreadEnvironmentWarning

JOIN_TIMEOUT = 2


def test_singleton() -> None:
    class MySingleton(metaclass=singletons.Singleton):
        pass

    a = MySingleton()
    b = MySingleton()

    assert a is b


@pytest.mark.parametrize('metaclass,queue_cls,process,repetitions', [
    (singletons.ProcessSingleton, multiprocessing.Queue, multiprocessing.Process, 8),
    (singletons.ThreadSingleton, queue.Queue, threading.Thread, 8),
])
def test_process_singleton(metaclass: Type, queue_cls: Type, process: Type, repetitions: int) -> None:
    class MySingleton(metaclass=metaclass):
        def __init__(self) -> None:
            self.uuid = uuid.uuid4()

    def inner_func(q: queue_cls) -> None:
        a = MySingleton()
        b = MySingleton()
        q.put((a.uuid, b.uuid,))

    test_q = queue_cls()
    processes = []
    for _ in range(repetitions):
        p = process(target=inner_func, args=(test_q,))
        p.start()
        processes.append(p)

    seen_uuids = set()
    while len(seen_uuids) < repetitions:
        a, b = test_q.get(timeout=JOIN_TIMEOUT)
        assert a == b
        assert a not in seen_uuids
        seen_uuids.add(a)


def test_greenthread_singleton_with_no_greenthreads():
    class MySingleton(metaclass=singletons.GreenthreadSingleton):
        pass

    with pytest.warns(NoGreenthreadEnvironmentWarning):
        a = MySingleton()
        b = MySingleton()
        assert a is b
