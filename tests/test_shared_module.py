import logging
import queue
import threading
from typing import Generator
from unittest.mock import Mock

import pytest
import shared
import singletons

JOIN_TIMEOUT = 2
THREADS = 8
LOG = logging.getLogger(__name__)


@pytest.fixture()
def _mock_shared() -> Generator:
    """Mock ``shared`` fixture."""
    shared.setup_mock()
    yield
    shared.teardown_mock()


def test_global():
    """Test actual global."""
    assert shared._mock is None
    a = shared.global_object()
    b = shared.global_object()
    assert a is b
    assert not isinstance(a, Mock)


@pytest.mark.usefixtures("_mock_shared")
def test_mocking_global():
    """Test mocking global."""
    assert shared._mock is not None
    assert isinstance(shared.global_object, singletons.GlobalFactory)
    a = shared.global_object()
    b = shared.global_object()
    assert a is b
    assert isinstance(a, Mock)


@pytest.mark.usefixtures("_mock_shared")
def test_mocking_simple():
    """Test mocking a simple object."""
    a = shared.simple_obj
    b = shared.simple_obj
    assert a is b
    assert isinstance(a, Mock)


@pytest.mark.usefixtures("_mock_shared")
def test_mocking_nonexistent_attr():
    """Test mocking a nonexistent attribute."""
    with pytest.raises(AttributeError):
        assert shared.nonexistent_obj


def test_thread():
    """Test actual thread."""

    def inner_func(q: queue.Queue) -> None:
        a = shared.thread_object()
        b = shared.thread_object()
        q.put((a, b))

    test_q = queue.Queue()
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=inner_func, args=(test_q,))
        t.start()
        threads.append(t)

    seen_ids = set()
    while len(seen_ids) < THREADS:
        a, b = test_q.get(timeout=JOIN_TIMEOUT)
        LOG.debug("Pulled %s, %s", a, b)
        assert a not in seen_ids
        assert a is b
        assert not isinstance(a, Mock)
        seen_ids.add(a)
        LOG.debug("seen_ids: %s", seen_ids)


@pytest.mark.usefixtures("_mock_shared")
def test_mocking_thread():
    """Test mocking thread."""

    def inner_func(q: queue.Queue) -> None:
        a = shared.thread_object()
        a.touch()
        LOG.debug(f"Touched thread_object %s", a)
        b = shared.thread_object()
        b.touch()
        LOG.debug(f"Touched thread_object %s", b)
        q.put((a, b))

    test_q = queue.Queue()
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=inner_func, args=(test_q,))
        t.start()
        threads.append(t)

    seen_ids = set()
    while len(seen_ids) < THREADS:
        a, b = test_q.get(timeout=JOIN_TIMEOUT)
        LOG.debug("Pulled %s, %s", a, b)
        assert a not in seen_ids
        assert a is b
        assert a.touch.call_count == 2
        seen_ids.add(a)
        LOG.debug("seen_ids: %s", seen_ids)


@pytest.mark.usefixtures("_mock_shared")
def test_reassign_mock():
    """Test reassigning mock."""
    a = object()
    shared.new_object = a
    assert shared.new_object is a


def test_reassign_no_mock():
    """Test actual reassigning."""
    a = object()
    shared.new_object = a
    assert shared.new_object is a
