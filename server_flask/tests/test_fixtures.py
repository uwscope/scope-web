import pytest

from scope.testing.test_fixtures_flask import *

pytest_plugins = [
    # Test against development configurations
    "scope.testing.config_dev",
    # Obtain necessary fixtures
    "scope.testing.fixtures_flask",
]


@pytest.fixture(name="testing_fixtures")
def fixture_testing_fixtures() -> bool:
    """
    Override to indicate we are testing fixtures.

    When True, fixtures should fail and explain the fixture failure.
    """

    return True
