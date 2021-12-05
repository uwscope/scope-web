import pytest
import requests
from typing import Callable

import scope.config


pytest_plugins = [
    # Test against development configurations
    "scope.testing.config_dev",
    # Obtain necessary fixtures
    "scope.testing.fixtures_flask",
]


def test_flask_session_unauthenticated_factory(
    config_flask_client: scope.config.FlaskClientConfig,
    test_flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    session = test_flask_session_unauthenticated_factory()
