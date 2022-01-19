import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


def test_app_config(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    # Obtain a session
    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "app/config",
        ),
    )

    assert response.ok

    config = response.json()

    # TODO: Anant: Define and check a schema

    assert "assessments" in config
    assert "lifeAreas" in config
    assert "resources" in config
