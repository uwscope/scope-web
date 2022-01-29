import pymongo.database
import pymongo.errors
import pytest
from typing import Callable


def test_compound_index_singletons(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test a basic indexing strategy for singleton documents.

    Assumes each document has a _type.
    All documents are singletons, so only one logical document exists for each type.
    As that logical document is modified, new documents are created with an incremented _rev field.
    """

    collection = database_temp_collection_factory()

    collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        unique=True,
        name="index",
    )

    # All of these singletons are valid
    result = collection.insert_many(
        [
            {"_type": "singleton", "_rev": "1"},
            {"_type": "singleton", "_rev": "2"},
            {"_type": "other singleton", "_rev": "1"},
            {"_type": "other singleton", "_rev": "2"},
        ]
    )
    assert len(result.inserted_ids) == 4

    # This should fail because the document already exists
    with pytest.raises(pymongo.errors.DuplicateKeyError) as exceptionInfo:
        collection.insert_one({"_type": "singleton", "_rev": "1"})
    assert exceptionInfo.value.code == 11000


def test_compound_index_singletons_and_sets(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test a basic indexing strategy for singleton documents and sets of documents.

    Assumes each document has a _type.

    Some documents are singletons, so only one logical document exists for each type.
    As that logical document is modified, new documents are created with an incremented _rev field.

    Other documents are sets, they have an additional _set_id for each logical document.
    As that logical document is modified, new documents are created with an incremented _rev field.

    This works for indexing, but it is possible to create both:
        {"_type": "type", "_rev": "1"},  # A singleton
        {"_type": "type", "_set_id": "1", "_rev": "1"},  # A set item

    The index does not prevent this, so it needs otherwise prevented or defined.
    """

    collection = database_temp_collection_factory()

    collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_set_id", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        unique=True,
        name="index",
    )

    # All of these singletons are valid
    result = collection.insert_many(
        [
            {"_type": "singleton", "_rev": "1"},
            {"_type": "singleton", "_rev": "2"},
            {"_type": "other singleton", "_rev": "1"},
            {"_type": "other singleton", "_rev": "2"},
        ]
    )
    assert len(result.inserted_ids) == 4

    # All of these set elements are valid
    result = collection.insert_many(
        [
            {"_type": "set", "_set_id": "1", "_rev": "1"},
            {"_type": "set", "_set_id": "1", "_rev": "2"},
            {"_type": "set", "_set_id": "2", "_rev": "1"},
            {"_type": "set", "_set_id": "2", "_rev": "2"},
            {"_type": "other set", "_set_id": "1", "_rev": "1"},
            {"_type": "other set", "_set_id": "1", "_rev": "2"},
        ]
    )
    assert len(result.inserted_ids) == 6

    # This should fail because the document already exists
    with pytest.raises(pymongo.errors.DuplicateKeyError) as exceptionInfo:
        collection.insert_one({"_type": "singleton", "_rev": "1"})
    assert exceptionInfo.value.code == 11000

    # This should fail because the document already exists
    with pytest.raises(pymongo.errors.DuplicateKeyError) as exceptionInfo:
        collection.insert_one({"_type": "set", "_set_id": "1", "_rev": "1"})
    assert exceptionInfo.value.code == 11000


def test_sparse_compound_index_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
):
    """
    Test a failed indexing strategy using different indices for each type and type_id.

    It was based in thinking sparse indices would allow this to work,
    but failed because sparse compound indices are applied if a document contains any of their keys.
    Some ability to filter documents before indexing would allow this to work,
    but DocumentDB does not apparently support such an ability.
    """

    collection = database_temp_collection_factory()

    # An index that might seem appropriate for a type which is a singleton.
    # Assumes storing documents of _type (e.g., a string) with a _rev (e.g., an integer).
    collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        unique=True,
        name="index_1",
    )

    # An index that might seem appropriate for another type with an id.
    # Assumes storing documents of _type_id (e.g., an integer) with a _rev (e.g., an integer).
    # We might think this will work because the index is sparse.
    collection.create_index(
        [
            ("_type_id", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        sparse=True,
        unique=True,
        name="index_2",
    )

    # This succeeds,
    # but the second index models _type_id value "null".
    # This happens even though the second index is sparse,
    # because a sparse compound index is applied if a document contains any of its keys.
    result = collection.insert_one(
        {
            "_type": "value",
            "_rev": "1",
            # "_type_id": null,
        }
    )
    assert result.inserted_id

    # This succeeds,
    # but the first index models _type value "null".
    # This always happens because the first index is not sparse.
    result = collection.insert_one(
        {
            "_type_id": "1",
            "_rev": "1",
            # "_type": null,
        }
    )
    assert result.inserted_id

    # This is ok with the first index,
    # but fails because the second index sees a duplicate with the first document.
    with pytest.raises(pymongo.errors.DuplicateKeyError) as exceptionInfo:
        result = collection.insert_one(
            {
                "_type": "other value",
                "_rev": "1",
                # "_type_id": null,
            }
        )
    assert exceptionInfo.value.code == 11000

    # This is ok with the second index,
    # but fails because the first index sees a duplicate with the second document.
    with pytest.raises(pymongo.errors.DuplicateKeyError) as exceptionInfo:
        result = collection.insert_one(
            {
                "_type_id": "2",
                "_rev": "1",
                # "_type": null,
            }
        )
    assert exceptionInfo.value.code == 11000
