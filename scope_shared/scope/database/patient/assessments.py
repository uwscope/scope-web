import copy
import datetime
import pymongo.collection
import pytz
from typing import List, Optional

import scope.database.collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.scheduled_assessments
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.schema
import scope.schema_utils as schema_utils

DOCUMENT_TYPE = "assessment"
SEMANTIC_SET_ID = "assessmentId"


def _calculate_scheduled_assessments_to_create(
    assessment_id: str,
    assessment: dict,
    maintenance_datetime: datetime.datetime,
) -> List[dict]:
    # Temporarily assume everybody is always in local timezone
    timezone = pytz.timezone("America/Los_Angeles")
    # Temporarily assume assessments are due at 8am, receive a reminder at 8am
    # Temporarily assume we should populate for the next 3 months

    if not assessment["assigned"]:
        return []

    # Create scheduled items
    new_scheduled_items = scheduled_item_utils.create_scheduled_items(
        start_datetime=date_utils.parse_datetime(assessment["assignedDateTime"]),
        effective_datetime=maintenance_datetime,
        has_repetition=True,  # If assigned, assessments are repeating
        frequency=assessment["frequency"],
        repeat_day_flags=None,  # Assessments do not have repeat_day_flags
        day_of_week=assessment.get("dayOfWeek", None),
        due_time_of_day=8,
        reminder=True,
        reminder_time_of_day=8,
        timezone=timezone,
        months=3,
    )

    # Fill in additional data needed for scheduled assessments
    new_scheduled_assessments = []
    for new_scheduled_item_current in new_scheduled_items:
        new_scheduled_assessment_current = copy.deepcopy(new_scheduled_item_current)

        new_scheduled_assessment_current.update(
            {
                "_type": scope.database.patient.scheduled_assessments.DOCUMENT_TYPE,
                SEMANTIC_SET_ID: assessment_id,
            }
        )

        new_scheduled_assessments.append(new_scheduled_assessment_current)

    return new_scheduled_assessments


def _calculate_scheduled_assessments_to_delete(
    scheduled_assessments: List[dict],
    assessment_id: str,
    maintenance_datetime: datetime.datetime,
) -> List[dict]:
    date_utils.raise_on_not_datetime_utc_aware(maintenance_datetime)

    current_scheduled_items = [
        scheduled_assessment_current
        for scheduled_assessment_current in scheduled_assessments
        if scheduled_assessment_current[SEMANTIC_SET_ID] == assessment_id
    ]

    pending_scheduled_items = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=current_scheduled_items,
        after_datetime=maintenance_datetime,
    )

    return pending_scheduled_items


def _maintain_pending_scheduled_assessments(
    collection: pymongo.collection.Collection,
    assessment_id: str,
    assessment: dict,
    maintenance_datetime: datetime.datetime,
):
    # Remove existing scheduled assessments as necessary
    existing_scheduled_assessments = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=collection
        )
    )
    if existing_scheduled_assessments:
        delete_items = _calculate_scheduled_assessments_to_delete(
            assessment_id=assessment_id,
            scheduled_assessments=existing_scheduled_assessments,
            maintenance_datetime=maintenance_datetime,
        )

        for delete_item_current in delete_items:
            scope.database.patient.scheduled_assessments.delete_scheduled_assessment(
                collection=collection,
                scheduled_assessment=delete_item_current,
                set_id=delete_item_current[
                    scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
                ],
            )

    # Create new scheduled assessments as necessary
    create_items = _calculate_scheduled_assessments_to_create(
        assessment_id=assessment_id,
        assessment=assessment,
        maintenance_datetime=maintenance_datetime,
    )
    if create_items:
        for create_item_current in create_items:
            schema_utils.assert_schema(
                data=create_item_current,
                schema=scope.schema.scheduled_assessment_schema,
            )

            scope.database.patient.scheduled_assessments.post_scheduled_assessment(
                collection=collection,
                scheduled_assessment=create_item_current,
            )


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

    # Enforce the schema
    schema_utils.raise_for_invalid_schema(
        data=assessment,
        schema=scope.schema.assessment_schema,
    )

    # Put the document
    assessment_set_put_result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=assessment,
    )

    #
    # Update the corresponding scheduled assessments
    #
    if assessment_set_put_result.inserted_count == 1:
        _maintain_pending_scheduled_assessments(
            collection=collection,
            assessment_id=set_id,
            assessment=assessment_set_put_result.document,
            maintenance_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
        )

    return assessment_set_put_result
