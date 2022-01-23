import pymongo.collection
from typing import Callable

import scope.database.collection_utils


def _configure_collection(*, collection: pymongo.collection.Collection) -> None:
    # Index structure based on test_index.py
    collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_set_id", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        unique=True,
        name="index",
    )

    # Populate some documents
    result = collection.insert_many(
        [
            {"_type": "singleton", "_rev": "1"},
            {"_type": "singleton", "_rev": "2"},
            {"_type": "other singleton", "_rev": "1"},
            {"_type": "other singleton", "_rev": "2"},
            {"_type": "set", "_set_id": "1", "_rev": "1"},
            {"_type": "set", "_set_id": "1", "_rev": "2"},
            {"_type": "set", "_set_id": "2", "_rev": "1"},
            {"_type": "set", "_set_id": "2", "_rev": "2"},
            {"_type": "other set", "_set_id": "1", "_rev": "1"},
            {"_type": "other set", "_set_id": "1", "_rev": "2"},
        ]
    )
    assert len(result.inserted_ids) == 10


def test_get_set(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a set.
    """
    collection = temp_collection_client_factory()
    _configure_collection(collection=collection)

    result = scope.database.collection_utils.get_set(
        collection=collection,
        document_type="set",
    )

    # Remove the "_id" field that was created upon insertion
    for result_current in result:
        del result_current["_id"]

    assert result == [
        {"_type": "set", "_set_id": "1", "_rev": "2"},
        {"_type": "set", "_set_id": "2", "_rev": "2"},
    ]


def test_get_set_not_found(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a set that does not exist.
    """
    collection = temp_collection_client_factory()
    _configure_collection(collection=collection)

    result = scope.database.collection_utils.get_set(
        collection=collection,
        document_type="nothing",
    )

    assert result is None


def test_get_set_element(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a set element.
    """
    collection = temp_collection_client_factory()
    _configure_collection(collection=collection)

    result = scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type="set",
        set_id="1",
    )

    # Remove the "_id" field that was created upon insertion
    del result["_id"]

    assert result == {"_type": "set", "_set_id": "1", "_rev": "2"}


def test_get_set_element_not_found(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a set element that does not exist.
    """
    collection = temp_collection_client_factory()
    _configure_collection(collection=collection)

    result = scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type="set",
        set_id="nothing",
    )

    assert result is None
