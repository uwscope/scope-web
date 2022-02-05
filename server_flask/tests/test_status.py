from typing import Callable
from urllib.parse import urljoin

import requests
import scope.config
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


def test_status(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "",
        ),
    )
    assert response.ok

    response_json = response.json()
    assert "status" in response_json
    assert response_json["status"] == 200
