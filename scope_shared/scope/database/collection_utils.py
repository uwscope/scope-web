import pymongo.collection
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
) -> dict:
    # Ensure retrieved _id can easily serialize
    doc_id = document.get("_id", None)
    if (doc_id is not None) and (not isinstance(doc_id, str)):
        document["_id"] = str(doc_id)

    return document


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
        replace_index = replace_index or existing_index.keys() != {"key", "ns", "unique", "valid"},
        replace_index = replace_index or existing_index["key"] != PRIMARY_COLLECTION_INDEX,
        replace_index = replace_index or existing_index["unique"] is not True,

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


def get_singleton(
    *,
    collection: pymongo.collection.Collection,
    doc_type: str,
) -> Optional[dict]:
    """
    Retrieve current document for singleton with "_type" of doc_type.

    If none exists, return None.
    """

    # Parameters in query pipeline
    query_document_type = doc_type

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
    result = _normalize_document(document=result)

    return result
