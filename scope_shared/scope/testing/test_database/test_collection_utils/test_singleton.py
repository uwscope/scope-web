import pymongo.collection
import pymongo.errors
import pytest
from typing import Callable

import scope.database.collection_utils


def _configure_collection_data(*, collection: pymongo.collection.Collection) -> None:
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
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a singleton.
    """
    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)
    _configure_collection_data(collection=collection)

    result = scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type="singleton",
    )

    # Remove the "_id" field that was created upon insertion
    del result["_id"]

    assert result == {"_type": "singleton", "_rev": "2"}


def test_get_singleton_not_found(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test retrieval of a singleton that does not exist.
    """
    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)
    _configure_collection_data(collection=collection)

    result = scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type="nothing",
    )

    assert result is None


@pytest.mark.parametrize(
    ["document"],
    [
        [
            {
                "_type": "singleton",
            }
        ],
        [{}],
    ],
    ids=[
        "with_type",
        "no_type",
    ],
)
def test_put_singleton(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    document: dict,
):
    """
    Test insert of a singleton.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    # Initial insert should generate "_rev" 1
    result = scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type="singleton",
        document=document,
    )

    assert result.inserted_count == 1
    assert result.inserted_id == result.document["_id"]

    del result.document["_id"]
    assert result.document == {
        "_type": "singleton",
        "_rev": 1,
    }

    # Second insert of same document should generate "_rev" 2
    result = scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type="singleton",
        document=document,
    )

    assert result.inserted_count == 1
    assert result.inserted_id == result.document["_id"]

    del result.document["_id"]
    assert result.document == {
        "_type": "singleton",
        "_rev": 2,
    }


def test_put_singleton_with_id_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Insert of an existing "_id" should fail, as this means document is already in the database.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.put_singleton(
            collection=collection,
            document_type="singleton",
            document={"_id": "not allowed"},
        )


def test_put_singleton_duplicate_rev_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Insert of an duplicate "_rev" should fail.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type="singleton",
        document={},
    )

    scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type="singleton",
        document={
            "_rev": 1,
        },
    )

    with pytest.raises(pymongo.errors.DuplicateKeyError):
        scope.database.collection_utils.put_singleton(
            collection=collection,
            document_type="singleton",
            document={},
        )

    with pytest.raises(pymongo.errors.DuplicateKeyError):
        scope.database.collection_utils.put_singleton(
            collection=collection,
            document_type="singleton",
            document={
                "_rev": 1,
            },
        )


def test_put_singleton_invalid_rev_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Insert of non-integer "_rev" should fail.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.put_singleton(
            collection=collection,
            document_type="singleton",
            document={
                "_rev": "1",
            },
        )
