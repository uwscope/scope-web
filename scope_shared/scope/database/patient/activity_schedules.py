import copy
import datetime
import pymongo.collection
import pytz
from typing import List, Optional

import scope.database.collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.scheduled_activities
import scope.database.patient.values
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils


DOCUMENT_TYPE = "activitySchedule"
SEMANTIC_SET_ID = "activityScheduleId"


def _calculate_scheduled_activities_to_create(
    activity_schedule_id: str,
    activity_schedule: dict,
    maintenance_datetime: datetime.datetime,
) -> List[dict]:
    # TODO: Temporarily assuming everybody is always in local timezone
    timezone = pytz.timezone("America/Los_Angeles")

    if activity_schedule["hasRepetition"]:
        frequency = scope.enums.ScheduledItemFrequency.Weekly.value
        months = 3
        repeat_day_flags = activity_schedule["repeatDayFlags"]
    else:
        frequency = None
        months = None
        repeat_day_flags = None

    if activity_schedule["hasReminder"]:
        reminder_time_of_day = activity_schedule["reminderTimeOfDay"]
    else:
        reminder_time_of_day = None

    # Create scheduled items
    new_scheduled_items = scheduled_item_utils.create_scheduled_items(
        start_date=date_utils.parse_date(activity_schedule["date"]),
        effective_datetime=maintenance_datetime,
        has_repetition=activity_schedule["hasRepetition"],
        frequency=frequency,
        repeat_day_flags=repeat_day_flags,
        day_of_week=None,  # Activities do not have dayOfWeek
        due_time_of_day=activity_schedule["timeOfDay"],
        reminder=activity_schedule["hasReminder"],
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
                SEMANTIC_SET_ID: activity_schedule_id,
                # "activityName": activity_schedule["name"],
            }
        )

        new_scheduled_activities.append(new_scheduled_activity_current)

    return new_scheduled_activities


def _calculate_scheduled_activities_to_delete(
    scheduled_activities: List[dict],
    activity_schedule_id: str,
    maintenance_datetime: datetime.datetime,
) -> List[dict]:
    date_utils.raise_on_not_datetime_utc_aware(maintenance_datetime)

    current_scheduled_items = [
        scheduled_activity_current
        for scheduled_activity_current in scheduled_activities
        if scheduled_activity_current[SEMANTIC_SET_ID] == activity_schedule_id
    ]

    pending_scheduled_items = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=current_scheduled_items,
        after_datetime=maintenance_datetime,
    )

    return pending_scheduled_items


def _maintain_pending_scheduled_activities(
    collection: pymongo.collection.Collection,
    activity_schedule_id: str,
    activity_schedule: dict,
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
                activity_schedule_id=activity_schedule_id,
                maintenance_datetime=maintenance_datetime,
            )

            # Mark all of them as deleted
            for delete_item_current in delete_items:
                scope.database.patient.scheduled_activities.delete_scheduled_activity(
                    collection=collection,
                    set_id=delete_item_current[
                        scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
                    ],
                    rev=delete_item_current.get("_rev"),
                )

    # Create new scheduled activities as necessary
    create_items = _calculate_scheduled_activities_to_create(
        activity_schedule_id=activity_schedule_id,
        activity_schedule=activity_schedule,
        maintenance_datetime=maintenance_datetime,
    )

    if create_items:
        data_snapshot = {}
        data_snapshot.update({"activitySchedule": activity_schedule})

        activity_data_snapshot = scope.database.patient.activities.get_activity(
            collection=collection,
            set_id=activity_schedule[scope.database.patient.activities.SEMANTIC_SET_ID],
        )
        data_snapshot.update({"activity": activity_data_snapshot})

        if activity_data_snapshot.get(
            scope.database.patient.values.SEMANTIC_SET_ID, None
        ):
            value_data_snapshot = scope.database.patient.values.get_value(
                collection=collection,
                set_id=activity_data_snapshot[
                    scope.database.patient.values.SEMANTIC_SET_ID
                ],
            )
            data_snapshot.update({"value": value_data_snapshot})

        for create_item_current in create_items:
            create_item_current = copy.deepcopy(create_item_current)

            create_item_current.update({"dataSnapshot": data_snapshot})
            schema_utils.assert_schema(
                data=create_item_current,
                schema=scope.schema.scheduled_activity_schema,
            )

            scope.database.patient.scheduled_activities.post_scheduled_activity(
                collection=collection, scheduled_activity=create_item_current
            )


def delete_activity_schedule(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
    rev: int,
) -> scope.database.collection_utils.SetPutResult:
    """
    Delete "activity-schedule" document.

    - Any corresponding ScheduledActivity documents must be deleted.
    """

    result = scope.database.collection_utils.delete_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
        rev=rev,
    )

    if result.inserted_count == 1:
        existing_scheduled_activities = (
            scope.database.patient.scheduled_activities.get_scheduled_activities(
                collection=collection
            )
        )

        # Perform only the delete component of maintenance
        delete_items = _calculate_scheduled_activities_to_delete(
            scheduled_activities=existing_scheduled_activities,
            activity_schedule_id=set_id,
            maintenance_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
        )

        # Delete the documents
        for delete_item_current in delete_items:
            scope.database.patient.scheduled_activities.delete_scheduled_activity(
                collection=collection,
                set_id=delete_item_current[
                    scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
                ],
                rev=delete_item_current.get("_rev"),
            )

    return result


def get_activity_schedules(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "activity-schedule" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_activity_schedule(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "activity-schedule" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_activity_schedule(
    *,
    collection: pymongo.collection.Collection,
    activity_schedule: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "activity-schedule" document.
    """

    activity_schedule_set_post_result = (
        scope.database.collection_utils.post_set_element(
            collection=collection,
            document_type=DOCUMENT_TYPE,
            semantic_set_id=SEMANTIC_SET_ID,
            document=activity_schedule,
        )
    )

    if activity_schedule_set_post_result.inserted_count == 1:
        _maintain_pending_scheduled_activities(
            collection=collection,
            activity_schedule_id=activity_schedule_set_post_result.inserted_set_id,
            activity_schedule=activity_schedule_set_post_result.document,
            maintenance_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
            delete_existing=False,
        )

    return activity_schedule_set_post_result


def put_activity_schedule(
    *,
    collection: pymongo.collection.Collection,
    activity_schedule: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "activity-schedule" document.
    """

    activity_schedule_set_put_result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=activity_schedule,
    )

    #
    # Update the corresponding scheduled activities
    #

    if activity_schedule_set_put_result.inserted_count == 1:
        _maintain_pending_scheduled_activities(
            collection=collection,
            activity_schedule_id=set_id,
            activity_schedule=activity_schedule_set_put_result.document,
            maintenance_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
            delete_existing=True,
        )

    return activity_schedule_set_put_result
