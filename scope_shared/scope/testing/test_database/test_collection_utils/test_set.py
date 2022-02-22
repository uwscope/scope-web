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

    assert result == {
        "_type": "set",
        "_set_id": "1",
        "_rev": "2",
    }


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
            }
        ],
        [{}],
    ],
    ids=[
        "with_type",
        "no_type",
    ],
)
@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_post_set_element(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    document: dict,
    semantic_set_id: Optional[str],
):
    """
    Test post of a set element.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    # Initial insert should generate "_rev" 1
    result = scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type="set",
        semantic_set_id=semantic_set_id,
        document=document,
    )
    assert result.inserted_count == 1

    document_expected = {
        "_id": result.inserted_id,
        "_type": "set",
        "_set_id": result.inserted_set_id,
        "_rev": 1,
    }
    if semantic_set_id:
        document_expected[semantic_set_id] = result.inserted_set_id

    assert result.document == document_expected


@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_post_set_element_with_id_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    semantic_set_id: Optional[str],
):
    """
    Post of an existing "_id" should fail, as this means document is already in the database.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.post_set_element(
            collection=collection,
            document_type="set",
            semantic_set_id=semantic_set_id,
            document={
                "_id": "not allowed",
            },
        )


@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_post_set_element_with_rev_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    semantic_set_id: Optional[str],
):
    """
    Post of an existing "_rev" should fail, as this means document is already in the database.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.post_set_element(
            collection=collection,
            document_type="set",
            semantic_set_id=semantic_set_id,
            document={
                "_rev": "not allowed",
            },
        )


@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_post_set_element_with_set_id_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    semantic_set_id: Optional[str],
):
    """
    Post of an existing "_set_id" should fail, as post expects to assign "_set_id".
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.post_set_element(
            collection=collection,
            document_type="set",
            semantic_set_id=semantic_set_id,
            document={
                "_set_id": "not allowed",
            },
        )

    if semantic_set_id:
        with pytest.raises(ValueError):
            scope.database.collection_utils.post_set_element(
                collection=collection,
                document_type="set",
                semantic_set_id=semantic_set_id,
                document={
                    semantic_set_id: "not allowed",
                },
            )


@pytest.mark.parametrize(
    ["document"],
    [
        [
            {
                "_type": "set",
                "_set_id": "set_id",
                "semanticSetId": "set_id",
            }
        ],
        [
            {
                "_type": "set",
                "_set_id": "set_id",
            }
        ],
        [
            {
                "_type": "set",
                "semanticSetId": "set_id",
            }
        ],
        [
            {
                "_set_id": "set_id",
                "semanticSetId": "set_id",
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
        [
            {
                "semanticSetId": "set_id",
            }
        ],
        [{}],
    ],
    ids=[
        "with_type_with_set_id_with_semanticSetId",
        "with_type_with_set_id",
        "with_type_with_semanticSetId",
        "with_set_id_with_semanticSetId",
        "with_type",
        "with_set_id",
        "with_semanticSetId",
        "empty",
    ],
)
@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_put_set_element(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    document: dict,
    semantic_set_id: Optional[str],
):
    """
    Test put of a set element.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    # Initial put should generate "_rev" 1
    result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type="set",
        semantic_set_id=semantic_set_id,
        set_id="set_id",
        document=document,
    )

    # Document we expect
    document_expected = copy.deepcopy(document)
    document_expected["_type"] = "set"
    document_expected["_set_id"] = "set_id"
    document_expected["_rev"] = 1
    if semantic_set_id:
        document_expected[semantic_set_id] = "set_id"

    # Document we obtained
    document = result.document
    assert result.inserted_count == 1
    assert result.inserted_id == document["_id"]
    del document["_id"]

    assert document == document_expected

    # Second put of same document should generate "_rev" 2
    result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type="set",
        semantic_set_id=semantic_set_id,
        set_id="set_id",
        document=document,
    )

    # Expect the increment to "_rev"
    document_expected["_rev"] = 2

    document = result.document
    assert result.inserted_count == 1
    assert result.inserted_id == document["_id"]
    del document["_id"]

    assert document == document_expected


@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_put_set_element_with_id_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    semantic_set_id: Optional[str],
):
    """
    Put of an existing "_id" should fail, as this means document is already in the database.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            semantic_set_id=semantic_set_id,
            set_id="set_id",
            document={
                "_id": "not allowed",
            },
        )


@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_put_set_element_duplicate_rev_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    semantic_set_id: Optional[str],
):
    """
    Put of a duplicate "_rev" should fail.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type="set",
        semantic_set_id=semantic_set_id,
        set_id="set_id",
        document={},
    )

    scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type="set",
        semantic_set_id=semantic_set_id,
        set_id="set_id",
        document={
            "_rev": 1,
        },
    )

    with pytest.raises(pymongo.errors.DuplicateKeyError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            semantic_set_id=semantic_set_id,
            set_id="set_id",
            document={},
        )

    with pytest.raises(pymongo.errors.DuplicateKeyError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            semantic_set_id=semantic_set_id,
            set_id="set_id",
            document={
                "_rev": 1,
            },
        )


@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_put_set_element_invalid_rev_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    semantic_set_id: Optional[str],
):
    """
    Put of non-integer "_rev" should fail.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            semantic_set_id=semantic_set_id,
            set_id="set_id",
            document={
                "_rev": "1",
            },
        )


@pytest.mark.parametrize(
    ["semantic_set_id"],
    [
        ["semanticSetId"],
        [None],
    ],
    ids=[
        "with_semantic_set_id",
        "without_semantic_set_id",
    ],
)
def test_put_set_element_mismatched_set_id_failure(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    semantic_set_id: Optional[str],
):
    """
    Put of existing but mismatched set id should fail.
    """

    collection = database_temp_collection_factory()
    scope.database.collection_utils.ensure_index(collection=collection)

    with pytest.raises(ValueError):
        scope.database.collection_utils.put_set_element(
            collection=collection,
            document_type="set",
            semantic_set_id=semantic_set_id,
            set_id="set_id",
            document={
                "_set_id": "invalid",
            },
        )

    if semantic_set_id:
        with pytest.raises(ValueError):
            scope.database.collection_utils.put_set_element(
                collection=collection,
                document_type="set",
                semantic_set_id=semantic_set_id,
                set_id="set_id",
                document={
                    semantic_set_id: "invalid",
                },
            )
