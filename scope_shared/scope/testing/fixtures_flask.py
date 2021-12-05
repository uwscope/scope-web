import pytest
import requests
from typing import Callable

import scope.config


def _flask_session_unauthenticated(
    *,
    config_flask_client: scope.config.FlaskClientConfig
) -> requests.Session:
    """
    Obtain a Flask session that is not authenticated.
    """

    session = requests.session()

    response = session.get(url=config_flask_client.baseurl)
    if response.status_code == 200:
        return session
    else:
        assert False


@pytest.fixture(name="flask_session_unauthenticated_factory")
def fixture_flask_session_unauthenticated_factory(
    request: pytest.FixtureRequest,
    config_flask_client: scope.config.FlaskClientConfig,
) -> Callable[[], requests.Session]:
    """
    Fixture for flask_session_unauthenticated_factory.
    """

    def factory() -> requests.Session:
        try:
            return _flask_session_unauthenticated(
                config_flask_client=config_flask_client,
            )
        except Exception:
            pytest.xfail("Failed in flask_session_unauthenticated_factory.")

    return factory


@pytest.fixture(name="test_flask_session_unauthenticated_factory")
def fixture_test_flask_session_unauthenticated_factory(
    request: pytest.FixtureRequest,
    config_flask_client: scope.config.FlaskClientConfig,
) -> Callable[[], requests.Session]:
    """
    Fixture for testing flask_session_unauthenticated_factory.
    """

    def factory() -> requests.Session:
        try:
            return _flask_session_unauthenticated(
                config_flask_client=config_flask_client,
            )
        except Exception:
            pytest.fail(
                "\n".join([
                    "Failed in flask_session_unauthenticated_factory.",
                    "Unable to obtain Flask session.",
                    "Flask expected at {}".format(config_flask_client.baseurl),
                ]),
                pytrace=False
            )

    return factory
