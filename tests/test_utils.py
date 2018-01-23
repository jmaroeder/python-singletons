import pytest

import singletons.utils


def test_greenthread_ident_default():
    assert singletons.utils.detect_greenthread_environment() == 'default'
    with pytest.raises(RuntimeError):
        print(singletons.utils.greenthread_ident())
