import aws_infrastructure.tasks.ssh
import pymongo.database
import pytest

import scope.config
import scope.documentdb.client
import scope.testing


def _fixture_database_client(
    *,
    explicit_check_fixtures: bool,
    documentdb_config: scope.config.DocumentDBConfig,
    documentdb_port_forward: aws_infrastructure.tasks.ssh.SSHPortForward,
    database_config: scope.config.DatabaseConfig,
) -> pymongo.database.Database:
    """
    Worker for fixture_database_client. Separated to allow fixture check for session scope.
    """

    # Allow catching any exception due to goal of fixture xfail
    #
    # noinspection PyBroadException
    try:
        #
        # Create the client
        #
        database_client = scope.documentdb.client.documentdb_client_database(
            # Connect via existing SSH port forward
            host="127.0.0.1",
            port=documentdb_port_forward.local_port,
            # Because of the port forward, must not attempt to access the replica set
            direct_connection=True,
            # DocumentDB requires SSL, but port forwarding means the certificate will not match
            tls_insecure=True,
            # Connect as database user
            user=database_config.user,
            password=database_config.password,
            # Desired database
            database_name=database_config.name
        )

        #
        # Probe the client
        #

        # Obtain list of collections in the database, this requires authentication
        response = database_client.list_collection_names()
        assert isinstance(response, list)

        return database_client
    except Exception:
        scope.testing.testing_check_fixtures(
            explicit_check_fixtures=explicit_check_fixtures,
            fixture_request=None,
            message="\n".join(
                [
                    "Failed in database_client.",
                    "Unable to obtain database client.",
                ]
            ),
        )


@pytest.fixture(name="database_client", scope="session")
def fixture_database_client(
    documentdb_config: scope.config.DocumentDBConfig,
    documentdb_port_forward: aws_infrastructure.tasks.ssh.SSHPortForward,
    database_config: scope.config.DatabaseConfig,
) -> pymongo.database.Database:
    """
    Fixture for obtaining a client for the database.

    Uses a single fixture for the entire session.
    """

    return _fixture_database_client(
        explicit_check_fixtures=False,
        documentdb_config=documentdb_config,
        documentdb_port_forward=documentdb_port_forward,
        database_config=database_config,
    )
