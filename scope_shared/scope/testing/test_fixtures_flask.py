import pytest
import requests
from typing import Callable

import scope.config


def test_flask_session_unauthenticated_factory(
    config_flask_client: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test for flask_session_unauthenticated_factory.
    """

    session = flask_session_unauthenticated_factory()
