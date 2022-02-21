from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "caseReview"
SEMANTIC_SET_ID = "caseReviewId"


def get_case_reviews(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "caseReview" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_case_review(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "caseReview" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_case_review(
    *,
    collection: pymongo.collection.Collection,
    case_review: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "caseReview" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=case_review,
    )


def put_case_review(
    *,
    collection: pymongo.collection.Collection,
    case_review: dict,
    set_id: str,
):
    """
    Put "caseReview" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
        semantic_set_id=SEMANTIC_SET_ID,
        document=case_review,
    )
