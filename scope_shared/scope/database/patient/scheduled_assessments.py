from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "scheduledAssessment"
SEMANTIC_SET_ID = "scheduledAssessmentId"


def get_scheduled_assessments(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "scheduleAssessment" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "scheduleAssessment" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    scheduled_assessment: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "scheduleAssessment" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=scheduled_assessment,
    )


def put_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    scheduled_assessment: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "scheduleAssessment" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=scheduled_assessment,
    )
