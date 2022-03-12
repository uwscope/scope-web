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


def _maintain_scheduled_assessments(
    collection: pymongo.collection.Collection,
    assessment_id: str,
    assessment: dict,
):
    # Remove existing scheduled items as necessary
    scheduled_items = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=collection
        )
    )
    if scheduled_items:
        # Filter to scheduled items for this assessment
        scheduled_items = [
            scheduled_assessment_current
            for scheduled_assessment_current in scheduled_items
            if scheduled_assessment_current[
                scope.database.patient.assessments.SEMANTIC_SET_ID
            ]
            == assessment_id
        ]

        # Identify which scheduled items are still pending
        pending_items = scheduled_item_utils.pending_scheduled_items(
            scheduled_items=scheduled_items,
            after_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
        )

        # Mark all of them as deleted
        for pending_item_current in pending_items:
            scope.database.patient.scheduled_assessments.delete_scheduled_assessment(
                collection=collection,
                scheduled_assessment=pending_item_current,
                set_id=pending_item_current[
                    scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
                ],
            )

    # Create new scheduled items as necessary

    # Temporarily assume everybody is always in local timezone
    timezone = pytz.timezone("America/Los_Angeles")
    # Temporarily assume assessments are due at 8am, receive a reminder at 8am
    # Temporarily assume we should populate for the next 3 months

    if assessment["assigned"]:
        new_scheduled_items = scheduled_item_utils.create_scheduled_items(
            start_date=date_utils.parse_datetime(assessment["assignedDateTime"])
            .astimezone(timezone)
            .date(),
            day_of_week=assessment["dayOfWeek"],
            frequency=assessment["frequency"],
            due_time_of_day=8,
            reminder=True,
            reminder_time_of_day=8,
            timezone=timezone,
            months=3,
        )

        for new_scheduled_item_current in new_scheduled_items:
            new_scheduled_assessment = copy.deepcopy(new_scheduled_item_current)

            new_scheduled_assessment.update(
                {
                    "_type": scope.database.patient.scheduled_assessments.DOCUMENT_TYPE,
                    scope.database.patient.assessments.SEMANTIC_SET_ID: assessment[
                        scope.database.patient.assessments.SEMANTIC_SET_ID
                    ],
                }
            )

            schema_utils.assert_schema(
                data=new_scheduled_assessment,
                schema=scope.schema.scheduled_assessment_schema,
            )

            scope.database.patient.scheduled_assessments.post_scheduled_assessment(
                collection=collection, scheduled_assessment=new_scheduled_assessment
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
        _maintain_scheduled_assessments(
            collection=collection,
            assessment_id=set_id,
            assessment=assessment_set_put_result.document,
        )

    return assessment_set_put_result
