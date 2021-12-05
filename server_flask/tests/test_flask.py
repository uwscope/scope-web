import requests
from typing import Callable

import scope.config


pytest_plugins = [
    # Test against development configurations
    "scope.testing.config_dev",
    # Obtain necessary fixtures
    "scope.testing.fixtures_flask",
]


def test_flask_session(
    config_flask_client: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    session = flask_session_unauthenticated_factory()

    response = session.get(config_flask_client.baseurl)
    assert response.ok
