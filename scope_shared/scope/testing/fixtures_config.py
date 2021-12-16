import pytest
import _pytest.python

import scope.config
import scope.testing.config


def pytest_generate_tests(metafunc: _pytest.python.Metafunc):
    """
    Configure fixture_testing_config for each testing context.

    Detect whether a module specifies a value for TESTING_CONFIGS.
    Otherwise, apply a default of ALL_CONFIGS.
    """
    if "_testing_config_generator" in metafunc.fixturenames:
        if 'TESTING_CONFIGS' in metafunc.module.__dict__:
            testing_configs = metafunc.module.TESTING_CONFIGS
        else:
            testing_configs = scope.testing.config.ALL_CONFIGS

        metafunc.parametrize(
            argnames="_testing_config_generator",
            argvalues=testing_configs.values(),
            ids=testing_configs.keys(),
        )


@pytest.fixture(
    name="testing_config",
)
def fixture_testing_config(
    _testing_config_generator: scope.testing.config.TestingConfig
) -> scope.testing.config.TestingConfig:
    """
    Primary fixture to parameterize testing for each TestingConfig.

    Designed with a unique parameter name for detection in pytest_generate_tests.
    """
    return _testing_config_generator


@pytest.fixture(
    name="flask_config",
)
def fixture_flask_config(
    testing_config: scope.testing.config.TestingConfig,
) -> scope.config.FlaskConfig:
    """
    Obtain Flask configuration.
    """
    return testing_config.flask_config


@pytest.fixture(
    name="flask_client_config",
)
def fixture_flask_client_config(
    flask_config: scope.config.FlaskConfig,
) -> scope.config.FlaskClientConfig:
    """
    Obtain Flask client configuration.
    """
    return scope.config.FlaskClientConfig(
        baseurl=flask_config.baseurl,
    )
