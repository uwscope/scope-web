import aws_infrastructure.tasks.ssh
import pytest
import _pytest.python

import scope.config
import scope.testing.testing_config


def pytest_generate_tests(metafunc: _pytest.python.Metafunc):
    """
    Configure fixture_testing_config for each testing context.

    Obtained desired testing configurations from module variable TESTING_CONFIGS.
    """
    if "_testing_config_generator" in metafunc.fixturenames:
        if "TESTING_CONFIGS" in metafunc.module.__dict__:
            testing_configs = metafunc.module.TESTING_CONFIGS
        else:
            raise ImportError(name="TESTING_CONFIGS not found in test module.")

        metafunc.parametrize(
            argnames="_testing_config_generator",
            argvalues=testing_configs,
            ids=[config.name for config in testing_configs],
            scope="session",
        )


@pytest.fixture(name="testing_config", scope="session")
def fixture_testing_config(
    _testing_config_generator: scope.testing.TestingConfig,
) -> scope.testing.TestingConfig:
    """
    Primary fixture to parameterize testing for each TestingConfig.

    Designed with a unique parameter name for detection in pytest_generate_tests.
    """
    return _testing_config_generator


@pytest.fixture(name="instance_ssh_config", scope="session")
def fixture_instance_ssh_config(
    testing_config: scope.testing.TestingConfig,
) -> aws_infrastructure.tasks.ssh.SSHConfig:
    """
    Obtain Instance SSH configuration.
    """
    return testing_config.instance_ssh_config


@pytest.fixture(name="documentdb_config", scope="session")
def fixture_documentdb_config(
    testing_config: scope.testing.TestingConfig,
) -> scope.config.DocumentDBConfig:
    """
    Obtain DocumentDB configuration.
    """
    return testing_config.documentdb_config


@pytest.fixture(name="documentdb_client_config", scope="session")
def fixture_documentdb_client_config(
    documentdb_config: scope.config.DocumentDBConfig,
) -> scope.config.DocumentDBClientConfig:
    """
    Obtain DocumentDBClient configuration.
    """
    return scope.config.DocumentDBClientConfig(
        endpoint=documentdb_config.endpoint,
        hosts=documentdb_config.hosts,
        port=documentdb_config.port,
    )


@pytest.fixture(name="database_config", scope="session")
def fixture_database_config(
    testing_config: scope.testing.TestingConfig,
) -> scope.config.DatabaseConfig:
    """
    Obtain database configuration.
    """
    return testing_config.database_config


@pytest.fixture(name="flask_config", scope="session")
def fixture_flask_config(
    testing_config: scope.testing.TestingConfig,
) -> scope.config.FlaskConfig:
    """
    Obtain Flask configuration.

    If a testing_config does not include a flask_config, skip any associated tests.
    """

    if testing_config.flask_config is None:
        pytest.skip(
            'No flask_config in testing_config "{}"'.format(testing_config.name)
        )

    return testing_config.flask_config


@pytest.fixture(name="flask_client_config", scope="session")
def fixture_flask_client_config(
    flask_config: scope.config.FlaskConfig,
) -> scope.config.FlaskClientConfig:
    """
    Obtain Flask client configuration.
    """
    return scope.config.FlaskClientConfig(
        baseurl=flask_config.baseurl,
    )
