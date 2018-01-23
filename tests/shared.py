import sys

import singletons


@singletons.GlobalFactory
def global_object():
    return object()


@singletons.ThreadFactory
def thread_object():
    return object()


simple_obj = object()


class _Shared(singletons.SharedModule):
    globals = globals()


sys.modules[__name__] = _Shared()
