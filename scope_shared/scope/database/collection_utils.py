from dataclasses import dataclass
import pymongo.collection
from typing import List
from typing import Optional


PRIMARY_COLLECTION_INDEX = [
    ("_type", pymongo.ASCENDING),
    ("_set_id", pymongo.ASCENDING),
    ("_rev", pymongo.DESCENDING),
]
PRIMARY_COLLECTION_INDEX_NAME = "_primary"


def _normalize_document(
    *,
    document: dict,
) -> None:
    """
    Currently implemented to modify document in place.
    """

    # Ensure retrieved _id can easily serialize
    doc_id = document.get("_id", None)
    if (doc_id is not None) and (not isinstance(doc_id, str)):
        document["_id"] = str(doc_id)


def delete_set_element(
    *,
    collection: pymongo.collection.Collection,
    document_type: str,
    set_id: str,
    destructive: bool,
) -> bool:
    # TODO: define semantics of this method, in place now so we're forced to use it

    if not destructive:
        raise NotImplementedError()

    # There is likely a race condition here, but our semantics for destructive deletion are weak.
    result = collection.delete_many(
        {
            "_type": document_type,
            "_set_id": set_id,
        }
    )

    return result.deleted_count > 0


def ensure_index(
    *,
    collection: pymongo.collection.Collection,
):
    """
    Ensure the expected index is present on this collection.
    """

    # Examine existing indices
    index_information = collection.index_information()

    # Remove any indices that are not expected
    indices_unexpected = set(index_information.keys()) - {
        "_id_",
        PRIMARY_COLLECTION_INDEX_NAME,
    }
    for index_unexpected in indices_unexpected:
        del index_information[index_unexpected]
        collection.drop_index(index_unexpected)

    # Determine if an existing index needs replaced
    if PRIMARY_COLLECTION_INDEX_NAME in index_information:
        existing_index = index_information[PRIMARY_COLLECTION_INDEX_NAME]

        replace_index = False
        if not replace_index:
            replace_index = existing_index.keys() != {"key", "ns", "unique", "valid"}
        if not replace_index:
            replace_index = existing_index["key"] != PRIMARY_COLLECTION_INDEX
        if not replace_index:
            replace_index = existing_index["unique"] is not True

        if replace_index:
            del index_information[PRIMARY_COLLECTION_INDEX_NAME]
            collection.drop_index(PRIMARY_COLLECTION_INDEX_NAME)

    # Create the index
    if PRIMARY_COLLECTION_INDEX_NAME not in index_information:
        collection.create_index(
            PRIMARY_COLLECTION_INDEX,
            unique=True,
            name=PRIMARY_COLLECTION_INDEX_NAME,
        )


def get_set(
    *,
    collection: pymongo.collection.Collection,
    document_type: str,
) -> Optional[List[dict]]:
    """
    Retrieve all elements of set with "_type" of document_type.

    If none exist, return None.
    """

    # Parameters in query pipeline
    query_document_type = document_type

    # Query pipeline
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
        # Confirm a result was found
        if not pipeline_result.alive:
            return None

        result = list(pipeline_result)

    # Normalize the results
    for result_current in result:
        _normalize_document(document=result_current)

    return result


def get_set_element(
    *,
    collection: pymongo.collection.Collection,
    document_type: str,
    set_id: str,
) -> Optional[dict]:
    """
    Retrieve all elements of set with "_type" document_type.

    If none exist, return None.
    """

    # Parameters in query pipeline
    query_document_type = document_type
    query_set_id = set_id

    # Query pipeline
    pipeline = [
        {
            "$match": {
                "_type": query_document_type,
                "_set_id": query_set_id,
            }
        },
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
        # Confirm a result was found
        if not pipeline_result.alive:
            return None

        result = pipeline_result.next()

    # Normalize the result
    _normalize_document(document=result)

    return result


def get_singleton(
    *,
    collection: pymongo.collection.Collection,
    document_type: str,
) -> Optional[dict]:
    """
    Retrieve current document for singleton with "_type" document_type.

    If none exists, return None.
    """

    # Parameters in query pipeline
    query_document_type = document_type

    # Query pipeline
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
        # Confirm a result was found
        if not pipeline_result.alive:
            return None

        result = pipeline_result.next()

    # Normalize the result
    _normalize_document(document=result)

    return result


# def put_set_element(
#     *,
#     collection: pymongo.collection.Collection,
#     document_type: str,
#     set_id: str,
# )
#
# def insert(
#     *,
#     collection: pymongo.collection.Collection,
#     document: dict,
# ) -> dict:
#     # TODO: define semantics of this method, in place now so we're forced to use it
#
#     result = collection.insert_one(document)
#
#     _normalize_document(document=document)
#
#     return document


@dataclass(frozen=True)
class PutResult:
    inserted_count: int
    inserted_id: str
    document: dict


def put_set_element(
    *,
    collection: pymongo.collection.Collection,
    document_type: str,
    set_id: str,
    document: dict
) -> PutResult:
    """
    Put a set element document.
    - Document must not already include an "_id".
    - An existing "_type" must match document_type.
    - An existing "_set_id" must match set_id.
    - An existing "_rev" will be incremented.
    """

    # Document must not include an "_id",
    # as this indicates it was retrieved from the database.
    if "_id" in document:
        raise ValueError("Document must not have existing \"_id\"")

    # If a document includes a "_type", it must match document_type.
    if "_type" in document:
        if document["_type"] != document_type:
            raise ValueError("document[\"_type\"] must match document_type")
    else:
        document["_type"] = document_type

    # If a document includes a "_set_id", it must match set_id.
    if "_set_id" in document:
        if document["_set_id"] != set_id:
            raise ValueError("document[\"_set_id\"] must match set_id")
    else:
        document["_set_id"] = set_id

    # Increment the "_rev"
    if "_rev" in document:
        if not isinstance(document["_rev"], int):
            raise ValueError("document[\"_rev\"] must be int")

        document["_rev"] += 1
    else:
        document["_rev"] = 1

    result = collection.insert_one(document=document)

    _normalize_document(document=document)

    return PutResult(
        inserted_count=1,
        inserted_id=str(result.inserted_id),
        document=document
    )


def put_singleton(
    *,
    collection: pymongo.collection.Collection,
    document_type: str,
    document: dict
) -> PutResult:
    """
    Put a singleton document.
    - Document must not already include an "_id".
    - An existing "_type" must match document_type.
    - An existing "_rev" will be incremented.
    """

    # Document must not include an "_id",
    # as this indicates it was retrieved from the database.
    if "_id" in document:
        raise ValueError("Document must not have existing \"_id\"")

    # If a document includes a "_type", it must match document_type.
    if "_type" in document:
        if document["_type"] != document_type:
            raise ValueError("document[\"_type\"] must match document_type")
    else:
        document["_type"] = document_type

    # Increment the "_rev"
    if "_rev" in document:
        if not isinstance(document["_rev"], int):
            raise ValueError("document[\"_rev\"] must be int")

        document["_rev"] += 1
    else:
        document["_rev"] = 1

    result = collection.insert_one(document=document)

    _normalize_document(document=document)

    return PutResult(
        inserted_count=1,
        inserted_id=str(result.inserted_id),
        document=document
    )
