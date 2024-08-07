from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "reviewMark"
SEMANTIC_SET_ID = "reviewMarkId"


def get_review_marks(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "reviewMark" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_review_mark(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "reviewMark" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_review_mark(
    *,
    collection: pymongo.collection.Collection,
    review_mark: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "reviewMark" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=review_mark,
    )


def put_review_mark(
    *,
    collection: pymongo.collection.Collection,
    review_mark: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "reviewMark" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=review_mark,
    )
