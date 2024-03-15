import copy

import pymongo.collection
import pymongo.errors
import pytest
from typing import Callable, Optional

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
            {"_type": "singleton", "_rev": 1},
            {"_type": "singleton", "_rev": 2},
            {"_type": "other singleton", "_rev": 1},
            {"_type": "other singleton", "_rev": 2},
            {"_type": "set", "_set_id": "1", "_rev": 1},
            {"_type": "set", "_set_id": "1", "_rev": 2},
            {"_type": "set", "_set_id": "2", "_rev": 1},
            {"_type": "set", "_set_id": "2", "_rev": 2},
            {"_type": "other set", "_set_id": "1", "_rev": 1},
            {"_type": "other set", "_set_id": "1", "_rev": 2},
            {"_type": "other set", "_set_id": "2", "_rev": 1},
            {"_type": "other set", "_set_id": "2", "_rev": 2},
            {"_type": "other set", "_set_id": "2", "_rev": 3, "_deleted": True},
        ]
    )
    assert len(result.inserted_ids) == 13


def test_get_multiple_types(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of multiple types from a collection.
    """
    collection = database_temp_collection_factory()
    _configure_collection(collection=collection)

    # We should match these results from obtaining individual singletons or sets
    result_singleton = scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type="singleton",
    )
    result_other_singleton = scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type="other singleton",
    )
    result_set = scope.database.collection_utils.get_set(
        collection=collection,
        document_type="set",
    )
    result_other_set = scope.database.collection_utils.get_set(
        collection=collection,
        document_type="other set",
    )

    result = scope.database.collection_utils.get_multiple_types(
        collection=collection,
        singleton_types=["singleton"],
        set_types=[],
    )
    assert result["singleton"] == result_singleton

    result = scope.database.collection_utils.get_multiple_types(
        collection=collection,
        singleton_types=[],
        set_types=["set"],
    )
    assert result["set"] == result_set

    result = scope.database.collection_utils.get_multiple_types(
        collection=collection,
        singleton_types=["nothing"],
        set_types=[],
    )
    assert result["nothing"] is None

    result = scope.database.collection_utils.get_multiple_types(
        collection=collection,
        singleton_types=[],
        set_types=["nothing"],
    )
    assert result["nothing"] == []

    result = scope.database.collection_utils.get_multiple_types(
        collection=collection,
        singleton_types=["other singleton", "nothing"],
        set_types=["other set"],
    )
    assert result["other singleton"] == result_other_singleton
    assert result["other set"] == result_other_set
    assert result["nothing"] is None
