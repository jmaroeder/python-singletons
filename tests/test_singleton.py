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


class MyProcessSingleton(metaclass=singletons.ProcessSingleton):
    def __init__(self) -> None:
        self.uuid = uuid.uuid4()


def process_inner_func(q: multiprocessing.Queue):
    a = MyProcessSingleton()
    b = MyProcessSingleton()
    q.put((a, b,))


class MyThreadSingleton(metaclass=singletons.ThreadSingleton):
    def __init__(self) -> None:
        self.uuid = uuid.uuid4()


def thread_inner_func(q: queue.Queue):
    a = MyThreadSingleton()
    b = MyThreadSingleton()
    q.put((a, b,))


@pytest.mark.parametrize('prefix,queue_cls,process,repetitions', [
    ('process', multiprocessing.Queue, multiprocessing.Process, 8),
    ('thread', queue.Queue, threading.Thread, 8),
])
def test_process_singleton(prefix: str, queue_cls: Type, process: Type, repetitions: int) -> None:
    test_q = queue_cls()
    processes = []
    for _ in range(repetitions):
        p = process(target=globals()[f'{prefix}_inner_func'], args=(test_q,))
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
