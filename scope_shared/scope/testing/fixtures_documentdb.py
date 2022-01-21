import aws_infrastructure.tasks.ssh
import pymongo
import pytest

import scope.config
import scope.documentdb.client
import scope.testing


@pytest.fixture(name="documentdb_port_forward", scope="session")
def fixture_documentdb_port_forward(
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig,
    documentdb_config: scope.config.DocumentDBConfig,
) -> aws_infrastructure.tasks.ssh.SSHPortForward:
    """
    Fixture for opening a local port that forwards to the DocumentDB cluster.

    Implemented separately from DocumentDB clients so multiple clients may share a port forward.

    Uses a single fixture for the entire session.

    TODO: Implement checks for the components of this fixture.

    Because of something in how port forwarding is implemented,
    attempting to split this out into a function that could be checked
    resulted in the test session hanging.
    Testing would hang in both success and failure.
    Likely culprit is the thread inside the port forward, which not may be terminating.
    Unclear why it does not also hang in this configuration, but low priority concern.
    """

    ssh_client = aws_infrastructure.tasks.ssh.SSHClient(ssh_config=instance_ssh_config)
    ssh_client.open()

    ssh_port_forward = aws_infrastructure.tasks.ssh.SSHPortForward(
        ssh_client=ssh_client,
        remote_host=documentdb_config.endpoint,
        remote_port=documentdb_config.port,
    )
    ssh_port_forward.open()

    yield ssh_port_forward

    ssh_port_forward.close()
    ssh_client.close()


def _fixture_documentdb_client_admin(
    *,
    explicit_check_fixtures: bool,
    documentdb_config: scope.config.DocumentDBConfig,
    documentdb_port_forward: aws_infrastructure.tasks.ssh.SSHPortForward,
) -> pymongo.MongoClient:
    """
    Worker for fixture_documentdb_client_admin. Separated to allow fixture check for session scope.
    """

    # Allow catching any exception due to goal of fixture xfail
    #
    # noinspection PyBroadException
    try:
        #
        # Create the client
        #
        documentdb_client_admin = scope.documentdb.client.documentdb_client_admin(
            # Connect via existing SSH port forward
            host="127.0.0.1",
            port=documentdb_port_forward.local_port,
            # Because of the port forward, must not attempt to access the replica set
            direct_connection=True,
            # DocumentDB requires SSL, but port forwarding means the certificate will not match
            tls_insecure=True,
            # Connect as admin
            admin_user=documentdb_config.admin_user,
            admin_password=documentdb_config.admin_password,
        )

        #
        # Probe the client
        #

        # Obtain list of collections in the admin database, this requires authentication
        response = documentdb_client_admin.admin.list_collection_names()
        assert isinstance(response, list)

        return documentdb_client_admin
    except Exception:
        scope.testing.testing_check_fixtures(
            explicit_check_fixtures=explicit_check_fixtures,
            fixture_request=None,
            message="\n".join(
                [
                    "Failed in documentdb_client_admin.",
                    "Unable to obtain DocumentDB client.",
                ]
            ),
        )


@pytest.fixture(name="documentdb_client_admin", scope="session")
def fixture_documentdb_client_admin(
    documentdb_config: scope.config.DocumentDBConfig,
    documentdb_port_forward: aws_infrastructure.tasks.ssh.SSHPortForward,
) -> pymongo.MongoClient:
    """
    Fixture for obtaining a client for the DocumentDB cluster, authenticated as the admin.

    Uses a single fixture for the entire session.
    """

    return _fixture_documentdb_client_admin(
        explicit_check_fixtures=False,
        documentdb_config=documentdb_config,
        documentdb_port_forward=documentdb_port_forward,
    )
