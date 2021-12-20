import pymongo
import pymongo.database
import pytest

import scope.config
import scope.testing


def _fixture_database_client(
    explicit_check_fixtures: bool,
    database_config: scope.config.DatabaseConfig,
    documentdb_client: pymongo.MongoClient,
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

        database_client = documentdb_client.get_database(database_config.name)

        #
        # Probe the client
        #

        # Ensure the database exists
        assert database_client.name in documentdb_client.list_database_names()

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
    database_config: scope.config.DatabaseConfig,
    documentdb_client_admin: pymongo.MongoClient,
) -> pymongo.database.Database:
    """
    Fixture for obtaining a client for the database.

    Uses a single fixture for the entire session.

    TODO: Use a fixture authenticated as the database user, rather than as admin.
    """

    return _fixture_database_client(
        explicit_check_fixtures=False,
        database_config=database_config,
        documentdb_client=documentdb_client_admin,
    )
