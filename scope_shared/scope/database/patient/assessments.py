from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils
import scope.database.patient.scheduled_assessments

DOCUMENT_TYPE = "assessment"
SEMANTIC_SET_ID = "assessmentId"


def get_assessments(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "assessment" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_assessment(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "assessment" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def put_assessment(
    *,
    collection: pymongo.collection.Collection,
    assessment: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "assessment" document.
    """

    assessment_set_put_result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=assessment,
    )

    assessment = assessment_set_put_result.document

    # TODO: Should these be only called "dayOfWeek" and "frequency" exist in assesment dict?
    scope.database.patient.scheduled_assessments.get_filter_and_put_scheduled_assessments(
        collection=collection,
        assessment=assessment,
    )

    # Create and post scheduled assessments.
    scope.database.patient.scheduled_assessments.create_and_post_scheduled_assessments(
        collection=collection,
        assessment=assessment,
        weeks=12,  # ~ 3 months
    )

    return assessment_set_put_result
