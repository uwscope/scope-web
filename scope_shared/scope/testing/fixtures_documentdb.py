import aws_infrastructure.tasks.ssh
import pymongo
import pytest

import scope.config


@pytest.fixture(name="documentdb_port_forward", scope="session")
def fixture_documentdb_port_forward(
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig,
    documentdb_config: scope.config.DocumentDBConfig,
) -> aws_infrastructure.tasks.ssh.SSHPortForward:
    """
    Fixture for opening a local port that forwards to the DocumentDB cluster.

    Implemented separately from DocumentDB clients so multiple clients may share a port forward.

    Uses a single fixture for the entire session.
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


@pytest.fixture(name="documentdb_client_admin", scope="session")
def fixture_documentdb_client_admin(
    request: pytest.FixtureRequest,
    documentdb_config: scope.config.DocumentDBConfig,
    documentdb_port_forward: aws_infrastructure.tasks.ssh.SSHPortForward,
) -> pymongo.MongoClient:
    """
    Fixture for obtain a client for the DocumentDB cluster, authenticated as the admin.

    Uses a single fixture for the entire session.
    """

    # Allow catching any exception due to goal of fixture xfail
    #
    # noinspection PyBroadException
    try:
        client_admin = pymongo.MongoClient(
            # Synchronously initiate the connection
            connect=True,
            # Connect via SSH port forward
            host="127.0.0.1",
            port=documentdb_port_forward.local_port,
            # Because of the port forward, must not attempt to access the replica set
            directConnection=True,
            # Connect as admin
            username=documentdb_config.admin_user,
            password=documentdb_config.admin_password,
            # DocumentDB requires SSL, but port forwarding means the certificate will not match
            tls=True,
            tlsInsecure=True,
        )

        # Ping the admin database, this does not require authentication
        response = client_admin.admin.command("ping")
        assert "ok" in response

        # Obtain list of collections in the admin database, this requires authentication
        response = client_admin.admin.list_collection_names()
        assert isinstance(response, list)

        return client_admin
    except Exception:
        if scope.testing.testing_check_fixtures(request=request):
            pytest.fail(
                "\n".join(
                    [
                        "Failed in documentdb_client_admin.",
                        "Unable to obtain DocumentDB client.",
                    ]
                ),
                pytrace=False,
            )
        else:
            pytest.xfail("Failed in documentdb_client_admin.")
