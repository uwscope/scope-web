import pymongo
import pymongo.database

import scope.config
import scope.testing.fixtures_database


def test_database_client(
    database_config: scope.config.DatabaseConfig,
    documentdb_client_admin: pymongo.MongoClient,
):
    """
    Test for database_client.

    TODO: Use a fixture authenticated as the database user, rather than as admin.
    """

    database_client = scope.testing.fixtures_database._fixture_database_client(
        explicit_check_fixtures=True,
        database_config=database_config,
        documentdb_client=documentdb_client_admin,
    )

    assert database_client is not None
