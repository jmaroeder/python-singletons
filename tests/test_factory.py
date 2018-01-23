import multiprocessing
import queue
import threading
import uuid
from typing import Callable, Type

import pytest

import singletons

JOIN_TIMEOUT = 2


def test_global_factory() -> None:
    @singletons.GlobalFactory
    def my_uuid():
        return uuid.uuid4()

    a = my_uuid()
    b = my_uuid()

    assert a is b


@pytest.mark.parametrize('factory,queue_cls,process,repetitions', [
    (singletons.ProcessFactory, multiprocessing.Queue, multiprocessing.Process, 8),
    (singletons.ThreadFactory, queue.Queue, threading.Thread, 8),
])
def test_process_factory(factory: Callable, queue_cls: Type, process: Type, repetitions: int) -> None:
    @factory
    def my_uuid():
        return uuid.uuid4()

    def inner_func(q: queue_cls) -> None:
        a = my_uuid()
        b = my_uuid()
        q.put((a, b,))

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
