from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils
import scope.database.patient.scheduled_assessments

DOCUMENT_TYPE = "assessmentLog"
SEMANTIC_SET_ID = "assessmentLogId"


def _maintain_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    assessment_log: dict,
):
    scheduled_assessment_id = assessment_log.get(
        scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID, None
    )
    if not scheduled_assessment_id:
        return

    scheduled_assessment_document = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessment(
            collection=collection,
            set_id=scheduled_assessment_id,
        )
    )
    if not scheduled_assessment_document:
        return

    scheduled_assessment_document["completed"] = True
    del scheduled_assessment_document["_id"]

    scheduled_assessment_put_result = (
        scope.database.patient.scheduled_assessments.put_scheduled_assessment(
            collection=collection,
            set_id=scheduled_assessment_id,
            scheduled_assessment=scheduled_assessment_document,
        )
    )

    return scheduled_assessment_put_result


def get_assessment_logs(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "assessmentLog" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_assessment_log(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "assessmentLog" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_assessment_log(
    *,
    collection: pymongo.collection.Collection,
    assessment_log: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "assessmentLog" document.
    """

    assessment_log_set_post_result = scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=assessment_log,
    )

    if assessment_log_set_post_result.inserted_count == 1:
        _maintain_scheduled_assessment(
            collection=collection,
            assessment_log=assessment_log_set_post_result.document,
        )

    return assessment_log_set_post_result


def put_assessment_log(
    *,
    collection: pymongo.collection.Collection,
    assessment_log: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "assessmentLog" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=assessment_log,
    )
