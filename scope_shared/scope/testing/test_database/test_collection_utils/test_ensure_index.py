import pymongo
import pymongo.collection
from typing import Callable

import scope.database.collection_utils


def test_index_creation(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test the expected index is created.
    """
    collection = temp_collection_client_factory()

    scope.database.collection_utils.ensure_index(collection=collection)

    index_information = collection.index_information()

    # Index should include "_id_" plus our desired index
    assert len(index_information) == 2
    assert "_id_" in index_information
    assert scope.database.collection_utils.PRIMARY_COLLECTION_INDEX_NAME in index_information

    # Check properties of our desired index
    index = index_information[scope.database.collection_utils.PRIMARY_COLLECTION_INDEX_NAME]
    assert index["key"] == scope.database.collection_utils.PRIMARY_COLLECTION_INDEX
    assert index["unique"]


def test_index_removal(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test an unexpected index will be removed.
    """
    collection = temp_collection_client_factory()

    collection.create_index(
        [
            ("_invalid", pymongo.ASCENDING)
        ],
        name="_invalid",
    )
    scope.database.collection_utils.ensure_index(collection=collection)

    index_information = collection.index_information()

    # Index should include "_id_" plus our desired index
    assert len(index_information) == 2
    assert "_id_" in index_information
    assert scope.database.collection_utils.PRIMARY_COLLECTION_INDEX_NAME in index_information


def test_index_replacement(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test an existing index with different properties will be replaced.
    """
    collection = temp_collection_client_factory()

    collection.create_index(
        [
            ("_invalid", pymongo.ASCENDING)
        ],
        name=scope.database.collection_utils.PRIMARY_COLLECTION_INDEX_NAME,
    )
    scope.database.collection_utils.ensure_index(collection=collection)

    index_information = collection.index_information()

    # Index should include "_id_" plus our desired index
    assert len(index_information) == 2
    assert "_id_" in index_information
    assert scope.database.collection_utils.PRIMARY_COLLECTION_INDEX_NAME in index_information
