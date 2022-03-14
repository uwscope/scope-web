import copy
import datetime
from typing import List, Optional
import pymongo.collection
import pytz

import scope.database.collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.scheduled_activities
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils


DOCUMENT_TYPE = "activity"
SEMANTIC_SET_ID = "activityId"


def _maintain_scheduled_activities(
    collection: pymongo.collection.Collection,
    activity_id: str,
    activity: dict,
    delete_existing: bool,
):

    if delete_existing:
        # Remove existing scheduled items as necessary
        scheduled_items = (
            scope.database.patient.scheduled_activities.get_scheduled_activities(
                collection=collection
            )
        )
        if scheduled_items:
            # Filter to scheduled items for this assessment
            scheduled_items = [
                scheduled_activity_current
                for scheduled_activity_current in scheduled_items
                if scheduled_activity_current[SEMANTIC_SET_ID] == activity_id
            ]

            # Identify which scheduled items are still pending
            pending_items = scheduled_item_utils.pending_scheduled_items(
                scheduled_items=scheduled_items,
                after_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
            )

            # Mark all of them as deleted
            for pending_item_current in pending_items:
                scope.database.patient.scheduled_activities.delete_scheduled_activity(
                    collection=collection,
                    scheduled_activity=pending_item_current,
                    set_id=pending_item_current[
                        scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
                    ],
                )

    # Temporarily assume everybody is always in local timezone
    timezone = pytz.timezone("America/Los_Angeles")

    if activity["isActive"]:
        new_scheduled_items = scheduled_item_utils.create_scheduled_items(
            start_date=date_utils.parse_datetime(activity["startDateTime"])
            .astimezone(timezone)
            .date(),
            has_repetition=activity["hasRepetition"],
            repeat_day_flags=activity.get("repeatDayFlags"),
            day_of_week=None,
            frequency=scope.enums.ScheduledItemFrequency.Weekly.value,
            due_time_of_day=activity["timeOfDay"],
            reminder=activity["hasReminder"],
            reminder_time_of_day=activity.get("reminderTimeOfDay"),
            timezone=timezone,
            months=3,
        )

        for new_scheduled_item_current in new_scheduled_items:
            new_scheduled_activity = copy.deepcopy(new_scheduled_item_current)

            new_scheduled_activity.update(
                {
                    "_type": scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
                    SEMANTIC_SET_ID: activity[SEMANTIC_SET_ID],
                    "activityName": activity["name"],
                }
            )

            schema_utils.assert_schema(
                data=new_scheduled_activity,
                schema=scope.schema.scheduled_activity_schema,
            )

            scope.database.patient.scheduled_activities.post_scheduled_activity(
                collection=collection, scheduled_activity=new_scheduled_activity
            )


def get_activities(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "activity" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_activity(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "activity" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_activity(
    *,
    collection: pymongo.collection.Collection,
    activity: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "activity" document.
    """

    activity_set_post_result = scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=activity,
    )

    # if activity_set_post_result.inserted_count == 1:

    #     _maintain_scheduled_activities(
    #         collection=collection,
    #         activity_id=activity_set_post_result.inserted_set_id,
    #         activity=activity_set_post_result.document,
    #         delete_existing=False,
    #     )

    return activity_set_post_result


def put_activity(
    *,
    collection: pymongo.collection.Collection,
    activity: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "activity" document.
    """

    activity_set_put_result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=activity,
    )
    #
    # Update the corresponding scheduled assessments
    #
    # if activity_set_put_result.inserted_count == 1:

    #     # NOTE: Update startDateTime here.
    #     # TODO: If "PUT", then if start_date is in past, reinitialize it as today, else leave it as it is.
    #     # TODO: We might not need it, might try disabling past date selections in client.

    #     _maintain_scheduled_activities(
    #         collection=collection,
    #         activity_id=set_id,
    #         activity=activity_set_put_result.document,
    #         delete_existing=True,
    #     )

    return activity_set_put_result
