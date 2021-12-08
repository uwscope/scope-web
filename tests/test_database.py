import aws_infrastructure.tasks.ssh
from pymongo import MongoClient
import pytest

import scope.config
import scope.testing.config


SSH_CONFIGS = {
    "host": aws_infrastructure.tasks.ssh.SSHConfig.load(
        ssh_config_path='./secrets/configuration/ssh.yaml',
    ),
}

DOCUMENTDB_CONFIGS = {
    "experimental": scope.config.DocumentDBConfig.load(
        config_path='./secrets/configuration/documentdb.yaml',
    ),
}


@pytest.fixture(
    name="config_ssh_client",
    # TODO: this won't allow modules to choose configurations
    params=SSH_CONFIGS.values(),
    ids=SSH_CONFIGS.keys(),
)
def fixture_config_ssh_client(
    request: pytest.FixtureRequest,
) -> aws_infrastructure.tasks.ssh.SSHConfig:
    """
    Obtain SSH client configuration.
    """
    return request.param


@pytest.fixture(
    name="config_documentdb",
    # TODO: this won't allow modules to choose configurations
    params=DOCUMENTDB_CONFIGS.values(),
    ids=DOCUMENTDB_CONFIGS.keys(),
)
def fixture_config_documentdb(
    request: pytest.FixtureRequest,
) -> scope.config.DocumentDBConfig:
    """
    Obtain DocumentDB configuration.
    """
    return request.param


@pytest.fixture(
    name="config_documentdb_client",
)
def fixture_config_documentdb_client(
    config_documentdb: scope.config.DocumentDBConfig,
) -> scope.config.DocumentDBClientConfig:
    """
    Obtain DocumentDB client configuration.
    """
    return scope.config.DocumentDBClientConfig(
        endpoint=config_documentdb.endpoint,
        hosts=config_documentdb.hosts,
        port=config_documentdb.port,
    )


def test_documentdb_reachable(
    config_ssh_client,
    config_documentdb,
):
    """
    Test that we can reach the DocumentDB cluster hosting the database.
    """

    with aws_infrastructure.tasks.ssh.SSHClientContextManager(ssh_config=config_ssh_client) as ssh_client:
        with aws_infrastructure.tasks.ssh.SSHPortForwardContextManager(
                ssh_client=ssh_client,
                remote_host=config_documentdb.endpoint,
                remote_port=config_documentdb.port,
        ) as ssh_port_forward:
            # Obtain a client authenticated as DocumentDB admin
            client_admin = MongoClient(
                # Synchronously initiate the connection
                connect=True,
                # Connect via SSH port forward
                host='127.0.0.1',
                port=ssh_port_forward.local_port,
                # Because of the port forward, must not attempt to access the replica set
                directConnection=True,
                # Connect as admin
                username=config_documentdb.admin_user,
                password=config_documentdb.admin_password,
                # DocumentDB requires SSL, but port forwarding means the certificate will not match
                tls=True,
                tlsInsecure=True,
            )

            # Ping the admin database, this does not require authentication
            response = client_admin.admin.command('ping')
            assert 'ok' in response

            # Obtain list of collections in the admin database, this requires authentication
            response = client_admin.admin.list_collection_names()
            assert isinstance(response, list)
