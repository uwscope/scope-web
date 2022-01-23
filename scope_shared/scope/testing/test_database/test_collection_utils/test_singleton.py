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


def test_get_singleton(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a singleton.
    """
    collection = temp_collection_client_factory()
    _configure_collection(collection=collection)

    result = scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type="singleton",
    )

    # Remove the "_id" field that was created upon insertion
    del result["_id"]

    assert result == {"_type": "singleton", "_rev": "2"}


def test_get_singleton_not_found(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a singleton that does not exist.
    """
    collection = temp_collection_client_factory()
    _configure_collection(collection=collection)

    result = scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type="nothing",
    )

    assert result is None
