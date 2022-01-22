import pytest
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS

# TODO: Implement authentication
pytest.skip("Authentication not implemented", allow_module_level=True)


def test_auth(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "auth",
        ),
    )
    assert response.ok

    assert response.json() == {
        "name": "Luke Skywalker",
        "authToken": "my token",
    }
