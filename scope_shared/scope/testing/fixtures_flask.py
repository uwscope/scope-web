import pytest
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import scope.testing


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
    request: pytest.FixtureRequest,
    flask_client_config: scope.config.FlaskClientConfig,
) -> Callable[[], requests.Session]:
    """
    Fixture for flask_session_unauthenticated_factory.

    Provides a factory for obtaining a Flask session that is not authenticated.
    """

    def factory() -> requests.Session:
        # Allow catching any exception due to goal of fixture xfail
        #
        # noinspection PyBroadException
        try:
            return _flask_session_unauthenticated(
                flask_client_config=flask_client_config,
            )
        except Exception:
            scope.testing.testing_check_fixtures(
                explicit_check_fixtures=None,
                fixture_request=request,
                message="\n".join(
                    [
                        "Failed in flask_session_unauthenticated_factory.",
                        "Unable to obtain Flask session.",
                    ]
                ),
            )

    return factory
