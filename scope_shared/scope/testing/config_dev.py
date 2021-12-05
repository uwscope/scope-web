import pytest

import scope.config
import scope.testing.config

@pytest.fixture(
    name="config_flask",
    params=scope.testing.config.FLASK_CONFIGS.values(),
    ids=scope.testing.config.FLASK_CONFIGS.keys(),
)
def fixture_config_flask(request: pytest.FixtureRequest) -> scope.config.FlaskConfig:
    """
    Obtain Flask configuration.
    """
    return request.param


@pytest.fixture(
    name="config_flask_client",
)
def fixture_config_flask_client(config_flask: scope.config.FlaskConfig) -> scope.config.FlaskClientConfig:
    """
    Obtain Flask client configuration.
    """
    return scope.config.FlaskClientConfig(
        baseurl=config_flask.baseurl,
    )
