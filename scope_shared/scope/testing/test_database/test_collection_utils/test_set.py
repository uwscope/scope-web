import pymongo.collection
import pymongo.errors
import pytest
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
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a set.
    """
    collection = database_temp_collection_factory()
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
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a set that does not exist.
    """
    collection = database_temp_collection_factory()
    _configure_collection(collection=collection)

    result = scope.database.collection_utils.get_set(
        collection=collection,
        document_type="nothing",
    )

    assert result is None


def test_get_set_element(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a set element.
    """
    collection = database_temp_collection_factory()
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
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a set element that does not exist.
    """
    collection = database_temp_collection_factory()
    _configure_collection(collection=collection)

    result = scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type="set",
        set_id="nothing",
    )

    assert result is None


@pytest.mark.parametrize(
    ["document"],
    [
        [
            {
                "_type": "set",
                "_set_id": "set_id",
            }
        ],
        [
            {
                "_type": "set",
            }
        ],
        [
            {
                "_set_id": "set_id",
            }
        ],
        [{}],
    ],
    ids=[
        "with_type_with_set_id",
        "with_type_no_set_id",
        "no_type_with_set_id",
        "no_type_no_set_id",
    ],
)
def test_put_set_element(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    document: dict,
):
    """
    Test insert of a set element.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    # Initial insert should generate "_rev" 1
    result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type="set",
        set_id="set_id",
        document=document,
    )

    document = result.document
    assert result.inserted_count == 1
    assert result.inserted_id == document["_id"]

    del document["_id"]
    assert document == {
        "_type": "set",
        "_set_id": "set_id",
        "_rev": 1,
    }

    # Second insert of same document should generate "_rev" 2
    result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type="set",
        set_id="set_id",
        document=document,
    )

    document = result.document
    assert result.inserted_count == 1
    assert result.inserted_id == document["_id"]

    del document["_id"]
    assert document == {
        "_type": "set",
        "_set_id": "set_id",
        "_rev": 2,
    }


def test_put_set_element_with_id_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Insert of an existing "_id" should fail, as this means document is already in the database.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            set_id="set_id",
            document={"_id": "not allowed"},
        )


def test_put_set_element_duplicate_rev_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Insert of an duplicate "_rev" should fail.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type="set",
        set_id="set_id",
        document={},
    )

    scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type="set",
        set_id="set_id",
        document={
            "_rev": 1,
        },
    )

    with pytest.raises(pymongo.errors.DuplicateKeyError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            set_id="set_id",
            document={},
        )

    with pytest.raises(pymongo.errors.DuplicateKeyError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            set_id="set_id",
            document={
                "_rev": 1,
            },
        )


def test_put_set_element_invalid_rev_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Insert of non-integer "_rev" should fail.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            set_id="set_id",
            document={
                "_rev": "1",
            },
        )
