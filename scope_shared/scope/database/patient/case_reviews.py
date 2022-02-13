from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "caseReview"
DOCUMENT_ID = "reviewId"


def get_case_reviews(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Retrieve list of "caseReview" document.
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
    Retrieve "caseReview" document.
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
) -> scope.database.collection_utils.PutResult:
    """
    Create the "caseReview" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=case_review[DOCUMENT_ID],
        document=case_review,
    )


def put_case_review(
    *,
    collection: pymongo.collection.Collection,
    case_review: dict,
):
    """
    Update the "caseReview" document.
    """
    # NOTE: Exactly same as post_case_review, but keeping it here if we need additional computation.

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=case_review[DOCUMENT_ID],
        document=case_review,
    )
