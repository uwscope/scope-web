from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "recentEntryReview"
SEMANTIC_SET_ID = "recentEntryReviewId"


def get_recent_entry_reviews(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "recentEntryReview" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_recent_entry_review(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "recentEntryReview" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_recent_entry_review(
    *,
    collection: pymongo.collection.Collection,
    recent_entry_review: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "recentEntryReview" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=recent_entry_review,
    )


def put_recent_entry_review(
    *,
    collection: pymongo.collection.Collection,
    recent_entry_review: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "recentEntryReview" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=recent_entry_review,
    )
