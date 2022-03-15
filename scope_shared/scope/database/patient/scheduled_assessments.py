import copy
from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils
import scope.database.patient.assessments
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils

DOCUMENT_TYPE = "scheduledAssessment"
SEMANTIC_SET_ID = "scheduledAssessmentId"


def get_scheduled_assessments(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "scheduledAssessment" documents.
    """

    scheduled_assessments = scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )

    if scheduled_assessments:
        scheduled_assessments = [
            scheduled_assessment_current
            for scheduled_assessment_current in scheduled_assessments
            if not scheduled_assessment_current.get("_deleted", False)
        ]

    return scheduled_assessments


def delete_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    scheduled_assessment: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    scheduled_assessment = copy.deepcopy(scheduled_assessment)

    scheduled_assessment["_deleted"] = True
    del scheduled_assessment["_id"]

    schema_utils.assert_schema(
        data=scheduled_assessment,
        schema=scope.schema.scheduled_assessment_schema,
    )

    return put_scheduled_assessment(
        collection=collection,
        scheduled_assessment=scheduled_assessment,
        set_id=set_id,
    )


def get_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "scheduleAssessment" document.
    """

    scheduled_assessment = scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )

    if scheduled_assessment:
        if scheduled_assessment.get("_deleted", False):
            scheduled_assessment = None

    return scheduled_assessment


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
