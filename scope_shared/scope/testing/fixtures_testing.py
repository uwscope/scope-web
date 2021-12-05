import pytest


@pytest.fixture(name="testing_fixtures")
def fixture_testing_fixtures() -> bool:
    """
    Fixture for whether we are currently testing our fixtures.

    When False, fixtures should xfail to avoid cluttering test results.
    When True, fixtures should fail and explain the fixture failure.
    """

    return False
