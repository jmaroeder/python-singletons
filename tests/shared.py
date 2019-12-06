import sys

import singletons


@singletons.GlobalFactory
def global_object() -> object:
    """Return a global object."""
    return object()


@singletons.ThreadFactory
def thread_object() -> object:
    """Return a thread object."""
    return object()


simple_obj = object()


class _Shared(singletons.SharedModule):
    globals = globals()  # noqa: A003


sys.modules[__name__] = _Shared()
