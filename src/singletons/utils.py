import contextlib
import os
import sys
import warnings

from singletons.exceptions import NoGreenthreadEnvironmentWarning

BOOLEAN_TRUE_STRINGS = frozenset(("true", "on", "ok", "y", "yes", "1"))
_greenthread_environment = None  # noqa: WPS121, WPS122


def _detect_greenthread_environment() -> str:
    """
    Detect if eventlet or gevent are in use.

    :return: 'eventlet', 'gevent', or 'default' (neither environment detected)
    """
    if "eventlet" in sys.modules:
        with contextlib.suppress(ImportError):
            from eventlet.patcher import is_monkey_patched  # noqa: WPS433
            import socket  # noqa: WPS433

            if is_monkey_patched(socket):
                return "eventlet"

    if "gevent" in sys.modules:
        with contextlib.suppress(ImportError):
            from gevent import socket as gsocket  # noqa: WPS433
            import socket  # noqa: WPS433, WPS440

            if socket.socket is gsocket.socket:  # type: ignore
                return "gevent"

    return "default"


def detect_greenthread_environment() -> str:
    """
    Detect the current greenthread environment.

    :return: 'eventlet', 'gevent', or 'default' (neither environment detected)
    """
    global _greenthread_environment  # noqa: WPS420
    if _greenthread_environment is None:
        _greenthread_environment = _detect_greenthread_environment()  # noqa: WPS122, WPS442
    return _greenthread_environment  # noqa: WPS121


def greenthread_ident() -> int:
    """
    Get the identifier of the current greenthread environment.

    :return: get_ident() or 0 if no greenthread environment is detected.
    """
    greenthread_environment = detect_greenthread_environment()
    if greenthread_environment == "eventlet":
        import eventlet.corolocal  # noqa: WPS433

        return eventlet.corolocal.get_ident()
    if greenthread_environment == "gevent":
        import gevent.thread  # noqa: WPS433

        return gevent.thread.get_ident()
    warnings.warn(
        "No greenthread environment detected - falling back to global scope",
        NoGreenthreadEnvironmentWarning,
    )
    return 0


def env_to_bool(key: str) -> bool:
    """
    Parse an environment variable and coerce it to a boolean value.

    :param key: the environment variable to use
    :return: the coerced bool value
    """
    str_value = os.environ.get(key, "")
    return str_value.strip().lower() in BOOLEAN_TRUE_STRINGS
