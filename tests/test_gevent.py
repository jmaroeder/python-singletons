import uuid
from typing import Type

import gevent
import gevent.queue
import pytest

import singletons
import singletons.singleton
import singletons.utils

JOIN_TIMEOUT = 2


@pytest.fixture
def force_gevent():
    singletons.utils._greenthread_environment = 'gevent'
    yield
    singletons.utils._greenthread_environment = None


@pytest.mark.usefixtures('force_gevent')
@pytest.mark.parametrize('metaclass,repetitions', [
    (singletons.GreenthreadSingleton, 10),
    (singletons.GeventSingleton, 10),
])
def test_greenthread_singleton(metaclass: Type, repetitions: int):
    assert singletons.detect_greenthread_environment() == 'gevent'

    class MySingleton(metaclass=metaclass):
        def __init__(self):
            self.uuid = uuid.uuid4()

    def inner_func(q: gevent.queue.Queue):
        a = MySingleton()
        b = MySingleton()
        q.put((a.uuid, b.uuid,))

    test_q = gevent.queue.Queue()
    greenthreads = []
    for _ in range(repetitions):
        p = gevent.spawn_raw(inner_func, test_q)
        greenthreads.append(p)
        gevent.sleep()  # force execution context to switch

    seen_uuids = set()
    while len(seen_uuids) < repetitions:
        a, b = test_q.get(timeout=JOIN_TIMEOUT)
        assert a == b
        assert a not in seen_uuids
        seen_uuids.add(a)
