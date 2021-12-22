import pymongo.database

import scope.database.patients


def test_patients_collection_exists(
    database_client: pymongo.database.Database,
):
    """
    Ensure the patients collection exists.
    """

    assert scope.database.patients.PATIENTS_COLLECTION_NAME in database_client.list_collection_names()
