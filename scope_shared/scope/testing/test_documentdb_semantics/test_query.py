import pymongo.database
import pymongo.errors
import pytest
from typing import Callable


def test_singleton_query(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Query a singleton.
    """

    collection = temp_collection_client_factory()

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

    # Query pipeline
    query_document_type = "singleton"
    pipeline = [
        {"$match": {"_type": query_document_type}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                "_id": None,
                "result": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$result"}},
    ]

    # Execute pipeline, obtain single result
    with collection.aggregate(pipeline) as pipeline_result:
        result = pipeline_result.next()

    # Remove the "_id" field that was created upon insertion
    del result["_id"]

    # Confirm expected result
    assert result == {"_type": "singleton", "_rev": "2"}


def test_set_query(
    temp_collection_client_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Query an element from a set.
    """

    collection = temp_collection_client_factory()

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

    # Query pipeline for all elements of a set
    query_document_type = "set"
    pipeline = [
        {"$match": {"_type": query_document_type}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                "_id": "$_set_id",
                "result": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$result"}},
    ]

    # Execute pipeline, obtain list of results
    with collection.aggregate(pipeline) as pipeline_result:
        result = list(pipeline_result)

    # Remove the "_id" field that was created upon insertion
    for result_current in result:
        del result_current["_id"]

    # Confirm expected result
    assert result == [
        {"_type": "set", "_set_id": "1", "_rev": "2"},
        {"_type": "set", "_set_id": "2", "_rev": "2"},
    ]

    # Query pipeline for single element of a set
    query_document_type = "set"
    query_set_id = "1"
    pipeline = [
        {"$match": {"_type": query_document_type, "_set_id": query_set_id}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                "_id": "$_set_id",
                "result": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$result"}},
    ]

    # Execute pipeline, obtain single result
    with collection.aggregate(pipeline) as pipeline_result:
        result = pipeline_result.next()

    # Remove the "_id" field that was created upon insertion
    del result["_id"]

    # Confirm expected result
    assert result == {"_type": "set", "_set_id": "1", "_rev": "2"}
