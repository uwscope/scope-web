import pytest
from typing import Optional


def testing_check_fixtures(
    *,
    explicit_check_fixtures: Optional[bool],
    fixture_request: Optional[pytest.FixtureRequest],
    message: str,
):
    """
    Whether we are currently executing within a fixture check.

    When False, fixtures can xfail to avoid cluttering test results.
    When True, fixtures should fail and explain the failure.
    """

    if explicit_check_fixtures is not None:
        check_fixtures = explicit_check_fixtures
    elif fixture_request is not None:
        if "TESTING_CHECK_FIXTURES" in fixture_request.module.__dict__:
            check_fixtures = fixture_request.module.__dict__["TESTING_CHECK_FIXTURES"]
        else:
            check_fixtures = False
    else:
        raise ValueError("Require explicit_check_fixtures or fixture_request.")

    if check_fixtures:
        pytest.fail(message, pytrace=False)
    else:
        pytest.xfail(message)
