import requests
from typing import Callable
from urllib.parse import urljoin

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

    assert response.json() == {
        "status": 200,
        "flask_status": "ok",
    }
