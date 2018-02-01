"""
Utility classes
"""
import os
import sys
import warnings

from singletons.exceptions import NoGreenthreadEnvironmentWarning

BOOLEAN_TRUE_STRINGS = {'true', 'on', 'ok', 'y', 'yes', '1', }
_greenthread_environment = None


def _detect_greenthread_environment() -> str:
    """
    Detect if eventlet or gevent are in use
    """
    if 'eventlet' in sys.modules:
        try:
            from eventlet.patcher import is_monkey_patched as is_eventlet
            import socket

            if is_eventlet(socket):
                return 'eventlet'
        except ImportError:
            pass

    if 'gevent' in sys.modules:
        try:
            from gevent import socket as _gsocket
            import socket

            if socket.socket is _gsocket.socket:
                return 'gevent'
        except ImportError:
            pass

    return 'default'


def detect_greenthread_environment() -> str:
    """
    Detect the current environment: eventlet, or gevent, or '' for default
    """
    global _greenthread_environment
    if _greenthread_environment is None:
        _greenthread_environment = _detect_greenthread_environment()
    return _greenthread_environment


def greenthread_ident() -> int:
    """
    Returns the identifier of the current greenthread environment, falls back to return 0 if no greenthread
    environment is detected
    """
    greenthread_environment = detect_greenthread_environment()
    if greenthread_environment == 'eventlet':
        import eventlet.corolocal  # pylint: disable=import-error
        return eventlet.corolocal.get_ident()
    if greenthread_environment == 'gevent':
        import gevent.thread  # pylint: disable=import-error
        return gevent.thread.get_ident()
    warnings.warn('No greenthread environment detected - falling back to global scope',
                  NoGreenthreadEnvironmentWarning)
    return 0


def env_to_bool(key: str) -> bool:
    """
    Parses an environment variable and coerces it to a boolean value
    """
    value = os.environ.get(key, '')
    return value.lower() in BOOLEAN_TRUE_STRINGS
