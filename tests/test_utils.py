import pytest

from singletons.exceptions import NoGreenthreadEnvironmentWarning
import singletons.utils


def test_greenthread_ident_default():
    assert singletons.utils.detect_greenthread_environment() == 'default'
    with pytest.warns(NoGreenthreadEnvironmentWarning):
        print(singletons.utils.greenthread_ident())
