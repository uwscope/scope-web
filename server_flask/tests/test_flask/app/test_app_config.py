import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import scope.schema
import scope.schema_utils as schema_utils
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

    # Remove "status" for schema validation
    assert "status" in config
    del config["status"]

    schema_utils.assert_schema(
        data=config,
        schema=scope.schema.app_config_schema,
    )


def test_app_quote(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    # Obtain a session
    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "app/quote",
        ),
    )

    assert response.ok

    response_json = response.json()
    assert "quote" in response_json
    assert type(response_json["quote"]) == str
