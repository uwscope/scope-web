import pymongo.database

import scope.database.patients
import scope.testing.test_database.test_collection_utils.test_ensure_index


def test_exists(
    database_client: pymongo.database.Database,
):
    """
    Ensure the patient identity collection exists.
    """

    assert (
        scope.database.patients.PATIENT_IDENTITY_COLLECTION
        in database_client.list_collection_names()
    )


def test_index_exists(
    database_client: pymongo.database.Database,
):
    """
    Ensure the patient identity collection has the expected index.
    """

    assert (
        scope.database.patients.PATIENT_IDENTITY_COLLECTION
        in database_client.list_collection_names()
    )

    collection = database_client.get_collection(
        scope.database.patients.PATIENT_IDENTITY_COLLECTION
    )

    scope.testing.test_database.test_collection_utils.test_ensure_index.assert_collection_utils_index(
        collection=collection
    )
