import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config


pytest_plugins = [
    # Test against development configurations
    "scope.testing.config_dev",
    # Obtain necessary fixtures
    "scope.testing.fixtures_flask",
]


def test_auth(
    config_flask_client: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            config_flask_client.baseurl,
            "auth",
        ),
    )
    assert response.ok

    assert response.json() == {
        "status": 200,
        "name": "Luke Skywalker",
        "authToken": "my token",
    }
