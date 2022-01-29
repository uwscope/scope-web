import pymongo
import pymongo.collection
from typing import Callable

import scope.database.collection_utils


def assert_collection_utils_index(*, collection: pymongo.collection.Collection):
    """
    Assert the provided collection has exactly our expected index.
    """

    index_information = collection.index_information()

    # Index should include "_id_" plus our desired index
    assert list(index_information.keys()) == [
        "_id_",
        scope.database.collection_utils.PRIMARY_COLLECTION_INDEX_NAME,
    ]

    # Check properties of our desired index
    index = index_information[
        scope.database.collection_utils.PRIMARY_COLLECTION_INDEX_NAME
    ]
    assert index["key"] == scope.database.collection_utils.PRIMARY_COLLECTION_INDEX
    assert index["unique"]


def test_index_creation(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test the expected index is created.
    """
    collection = database_temp_collection_factory()

    scope.database.collection_utils.ensure_index(collection=collection)

    assert_collection_utils_index(collection=collection)


def test_index_removal(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test an unexpected index will be removed.
    """
    collection = database_temp_collection_factory()

    collection.create_index(
        [("_invalid", pymongo.ASCENDING)],
        name="_invalid",
    )
    scope.database.collection_utils.ensure_index(collection=collection)

    assert_collection_utils_index(collection=collection)


def test_index_replacement(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test an existing index with different properties will be replaced.
    """
    collection = database_temp_collection_factory()

    collection.create_index(
        [("_invalid", pymongo.ASCENDING)],
        name=scope.database.collection_utils.PRIMARY_COLLECTION_INDEX_NAME,
    )
    scope.database.collection_utils.ensure_index(collection=collection)

    assert_collection_utils_index(collection=collection)
