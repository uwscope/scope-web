import pytest

def testing_check_fixtures(request: pytest.FixtureRequest) -> bool:
    """
    Whether we are currently checking our fixtures.

    When False, fixtures can xfail to avoid cluttering test results.
    When True, fixtures should fail and explain the failure.
    """

    if "TESTING_CHECK_FIXTURES" in request.module.__dict__:
        return request.module.__dict__["TESTING_CHECK_FIXTURES"]
    else:
        return False
