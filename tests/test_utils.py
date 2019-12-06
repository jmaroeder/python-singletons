import pytest
import singletons.utils
from singletons.exceptions import NoGreenthreadEnvironmentWarning


def test_greenthread_ident_default():
    """Test greenthread_ident() when there is no greenthread environment."""
    assert singletons.utils.detect_greenthread_environment() == "default"
    with pytest.warns(NoGreenthreadEnvironmentWarning):
        assert singletons.utils.greenthread_ident() is not None
