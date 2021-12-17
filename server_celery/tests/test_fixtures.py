"""
This module tests fixtures underlying many other tests.
Many such fixtures xfail if a condition is not met, preventing verbose output of many tests failing.
This module overrides "testing_fixtures" so that fixtures can know they are being tested.
Fixtures should then fail instead of xfail, allowing inspection of the failure.

Current fixture tests are imported from "scope.testing.test_fixtures".
"""

import pytest

from scope.testing.test_fixtures import *
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


@pytest.fixture(name="testing_fixtures")
def fixture_testing_fixtures() -> bool:
    """
    Override to indicate we are testing fixtures.

    When True, fixtures should fail and explain the fixture failure.
    """

    return True
