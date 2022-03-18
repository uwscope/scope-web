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


def _calculate_scheduled_activities_to_create(
    activity_id: str,
    activity: dict,
    maintenance_datetime: datetime.datetime,
) -> List[dict]:
    # Temporarily assume everybody is always in local timezone
    timezone = pytz.timezone("America/Los_Angeles")

    if any([not activity["isActive"], activity["isDeleted"]]):
        return []

    if activity["hasRepetition"]:
        frequency = scope.enums.ScheduledItemFrequency.Weekly.value
        months = 3
        repeat_day_flags = activity["repeatDayFlags"]
    else:
        frequency = None
        months = None
        repeat_day_flags = None

    if activity["hasReminder"]:
        reminder_time_of_day = activity["reminderTimeOfDay"]
    else:
        reminder_time_of_day = None

    # Create scheduled items
    new_scheduled_items = scheduled_item_utils.create_scheduled_items(
        start_datetime=date_utils.parse_datetime(activity["startDateTime"]),
        effective_datetime=maintenance_datetime,
        has_repetition=activity["hasRepetition"],
        frequency=frequency,
        repeat_day_flags=repeat_day_flags,
        day_of_week=None,  # Activities do not have dayOfWeek
        due_time_of_day=activity["timeOfDay"],
        reminder=activity["hasReminder"],
        reminder_time_of_day=reminder_time_of_day,
        timezone=timezone,
        months=months,
    )

    # Fill in additional data needed for scheduled activities
    new_scheduled_activities = []
    for new_scheduled_item_current in new_scheduled_items:
        new_scheduled_activity_current = copy.deepcopy(new_scheduled_item_current)

        new_scheduled_activity_current.update(
            {
                "_type": scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
                SEMANTIC_SET_ID: activity_id,
                "activityName": activity["name"],
            }
        )

        new_scheduled_activities.append(new_scheduled_activity_current)

    return new_scheduled_activities


def _calculate_scheduled_activities_to_delete(
    scheduled_activities: List[dict],
    activity_id: str,
    maintenance_datetime: datetime.datetime,
) -> List[dict]:
    date_utils.raise_on_not_datetime_utc_aware(maintenance_datetime)

    current_scheduled_items = [
        scheduled_activity_current
        for scheduled_activity_current in scheduled_activities
        if scheduled_activity_current[SEMANTIC_SET_ID] == activity_id
    ]

    pending_scheduled_items = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=current_scheduled_items,
        after_datetime=maintenance_datetime,
    )

    return pending_scheduled_items


def _maintain_pending_scheduled_activities(
    collection: pymongo.collection.Collection,
    activity_id: str,
    activity: dict,
    maintenance_datetime: datetime.datetime,
    delete_existing: bool,
):
    # Delete existing will be False if we are already certain
    # that no existing scheduled activities need deleted as part of maintenance.
    # This would be the case in a post of a new activity.
    if delete_existing:
        # Remove existing scheduled activities as necessary
        existing_scheduled_activities = (
            scope.database.patient.scheduled_activities.get_scheduled_activities(
                collection=collection
            )
        )
        if existing_scheduled_activities:
            delete_items = _calculate_scheduled_activities_to_delete(
                scheduled_activities=existing_scheduled_activities,
                activity_id=activity_id,
                maintenance_datetime=maintenance_datetime,
            )

            # Mark all of them as deleted
            for delete_item_current in delete_items:
                scope.database.patient.scheduled_activities.delete_scheduled_activity(
                    collection=collection,
                    scheduled_activity=delete_item_current,
                    set_id=delete_item_current[
                        scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
                    ],
                )

    # Create new scheduled activities as necessary
    create_items = _calculate_scheduled_activities_to_create(
        activity_id=activity_id,
        activity=activity,
        maintenance_datetime=maintenance_datetime,
    )
    if create_items:
        for create_item_current in create_items:
            schema_utils.assert_schema(
                data=create_item_current,
                schema=scope.schema.scheduled_activity_schema,
            )

            scope.database.patient.scheduled_activities.post_scheduled_activity(
                collection=collection, scheduled_activity=create_item_current
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

    if activity_set_post_result.inserted_count == 1:
        _maintain_pending_scheduled_activities(
            collection=collection,
            activity_id=activity_set_post_result.inserted_set_id,
            activity=activity_set_post_result.document,
            maintenance_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
            delete_existing=False,
        )

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
    # Update the corresponding scheduled activities
    #

    if activity_set_put_result.inserted_count == 1:
        _maintain_pending_scheduled_activities(
            collection=collection,
            activity_id=set_id,
            activity=activity_set_put_result.document,
            maintenance_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
            delete_existing=True,
        )

    return activity_set_put_result
