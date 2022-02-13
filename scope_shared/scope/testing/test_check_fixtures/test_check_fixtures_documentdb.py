import aws_infrastructure.tasks.ssh

import scope.config
import scope.testing.fixtures_documentdb


def test_documentdb_client_admin(
    documentdb_config: scope.config.DocumentDBConfig,
    documentdb_port_forward: aws_infrastructure.tasks.ssh.SSHPortForward,
):
    """
    Test for documentdb_client_admin.
    """
    documentdb_client_admin = scope.testing.fixtures_documentdb._fixture_documentdb_client_admin(
        explicit_check_fixtures=True,
        documentdb_config=documentdb_config,
        documentdb_port_forward=documentdb_port_forward,
    )  # fmt:skip

    assert documentdb_client_admin is not None
