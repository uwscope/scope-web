import aws_infrastructure.tasks.ssh
import scope.config
from pymongo import MongoClient

import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


def test_documentdb_reachable(
    documentdb_config: scope.config.DocumentDBConfig,
    documentdb_port_forward: aws_infrastructure.tasks.ssh.SSHPortForward,
):
    """
    Test that we can reach the DocumentDB cluster hosting the database.
    """

    # Obtain a client authenticated as DocumentDB admin
    client_admin = MongoClient(
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
