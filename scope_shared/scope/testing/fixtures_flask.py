import pytest
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config


pytest_plugins = [
    "scope.testing.fixtures_config",
    "scope.testing.fixtures_testing",
]


def _flask_session_unauthenticated(
    *,
    flask_client_config: scope.config.FlaskClientConfig,
) -> requests.Session:
    """
    Obtain a Flask session that is not authenticated.
    """

    session = requests.session()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "",
        ),
    )
    assert response.ok

    return session


@pytest.fixture(name="flask_session_unauthenticated_factory")
def fixture_flask_session_unauthenticated_factory(
    flask_client_config: scope.config.FlaskClientConfig,
    testing_fixtures: bool,
) -> Callable[[], requests.Session]:
    """
    Fixture for flask_session_unauthenticated_factory.

    Provides a factory for obtaining Flask sessions that are not authenticated.
    """

    def factory() -> requests.Session:
        # Allow catching any exception due to goal of fixture xfail
        # noinspection PyBroadException
        try:
            return _flask_session_unauthenticated(
                flask_client_config=flask_client_config,
            )
        except Exception:
            if testing_fixtures:
                pytest.fail(
                    "\n".join(
                        [
                            "Failed in flask_session_unauthenticated_factory.",
                            "Unable to obtain Flask session.",
                            "Flask expected at {}".format(flask_client_config.baseurl),
                        ]
                    ),
                    pytrace=False,
                )
            else:
                pytest.xfail("Failed in flask_session_unauthenticated_factory.")

    return factory
