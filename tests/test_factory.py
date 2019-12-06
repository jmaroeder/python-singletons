import multiprocessing
import queue
import threading
import uuid
from typing import Type

import pytest
import singletons
from singletons.exceptions import NoGreenthreadEnvironmentWarning

JOIN_TIMEOUT = 2


def test_global_factory() -> None:
    """Test GlobalFactory."""

    @singletons.GlobalFactory
    def my_uuid():
        return uuid.uuid4()

    a = my_uuid()
    b = my_uuid()

    assert a is b


@singletons.ProcessFactory
def process_my_uuid():
    """Get a uuid per Process."""
    return uuid.uuid4()


def process_inner_func(q: multiprocessing.Queue):
    """Helper function for testing ProcessFactory."""
    a = process_my_uuid()
    b = process_my_uuid()
    q.put((a, b))


@singletons.ThreadFactory
def thread_my_uuid():
    """Get a uuid per Thread."""
    return uuid.uuid4()


def thread_inner_func(q: queue.Queue):
    """Helper function for testing ThreadFactory."""
    a = thread_my_uuid()
    b = thread_my_uuid()
    q.put((a, b))


@pytest.mark.parametrize(
    ("prefix", "queue_cls", "process", "repetitions"),
    [
        ("process", multiprocessing.Queue, multiprocessing.Process, 8),
        ("thread", queue.Queue, threading.Thread, 8),
    ],
)
def test_process_factory(prefix: str, queue_cls: Type, process: Type, repetitions: int) -> None:
    """Test Process and Thread Factories."""
    test_q = queue_cls()
    processes = []
    for _ in range(repetitions):
        p = process(target=globals()[f"{prefix}_inner_func"], args=(test_q,))
        p.start()
        processes.append(p)

    seen_uuids = set()
    while len(seen_uuids) < repetitions:
        a, b = test_q.get(timeout=JOIN_TIMEOUT)
        assert a == b
        assert a not in seen_uuids
        seen_uuids.add(a)


def test_greenthread_factory_with_no_greenthreads():
    """Test Greenthread Factory when there are no greenthread libraries enabled."""

    @singletons.GreenthreadFactory
    def my_uuid():
        """Get a uuid per greenthread."""
        return uuid.uuid4()

    with pytest.warns(NoGreenthreadEnvironmentWarning):
        a = my_uuid()
        b = my_uuid()
        assert a is b
