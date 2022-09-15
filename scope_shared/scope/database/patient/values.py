from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "value"
SEMANTIC_SET_ID = "valueId"


def get_values(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "value" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_value(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "value" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_value(
    *,
    collection: pymongo.collection.Collection,
    value: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "value" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=value,
    )


def put_value(
    *,
    collection: pymongo.collection.Collection,
    value: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "value" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=value,
    )
