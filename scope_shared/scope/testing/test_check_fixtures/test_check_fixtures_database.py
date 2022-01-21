import aws_infrastructure.tasks.ssh

import scope.config
import scope.testing.fixtures_database


def test_database_client(
    documentdb_config: scope.config.DocumentDBConfig,
    documentdb_port_forward: aws_infrastructure.tasks.ssh.SSHPortForward,
    database_config: scope.config.DatabaseConfig,
):
    """
    Test for database_client.
    """

    database_client = scope.testing.fixtures_database._fixture_database_client(
        explicit_check_fixtures=True,
        documentdb_config=documentdb_config,
        documentdb_port_forward=documentdb_port_forward,
        database_config=database_config,
    )

    assert database_client is not None
