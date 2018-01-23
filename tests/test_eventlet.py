import uuid
from typing import Type

import eventlet
import pytest

import singletons
import singletons.singleton
import singletons.utils

JOIN_TIMEOUT = 2


@pytest.fixture
def force_eventlet():
    singletons.utils._greenthread_environment = 'eventlet'
    yield
    singletons.utils._greenthread_environment = None


@pytest.mark.usefixtures('force_eventlet')
@pytest.mark.parametrize('metaclass,repetitions', [
    (singletons.GreenthreadSingleton, 10),
    (singletons.EventletSingleton, 10),
])
def test_greenthread_singleton(metaclass: Type, repetitions: int):
    assert singletons.detect_greenthread_environment() == 'eventlet'

    class MySingleton(metaclass=metaclass):
        def __init__(self):
            self.uuid = uuid.uuid4()

    def inner_func(q: eventlet.Queue):
        a = MySingleton()
        b = MySingleton()
        q.put((a.uuid, b.uuid,))

    test_q = eventlet.Queue()
    greenthreads = []
    for _ in range(repetitions):
        p = eventlet.spawn_n(inner_func, test_q)
        greenthreads.append(p)
        eventlet.sleep()  # force execution context to switch

    seen_uuids = set()
    while len(seen_uuids) < repetitions:
        a, b = test_q.get(timeout=JOIN_TIMEOUT)
        assert a == b
        assert a not in seen_uuids
        seen_uuids.add(a)
