import copy
import datetime
from typing import List, Optional
import pymongo.collection

import scope.database.collection_utils
import scope.database.patient.activities
import scope.database.patient.activity_schedules
import scope.database.patient.values
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.schema

DOCUMENT_TYPE = "scheduledActivity"
SEMANTIC_SET_ID = "scheduledActivityId"
DATA_SNAPSHOT_PROPERTY = "dataSnapshot"


def build_data_snapshot(
    *,
    activity_schedule_id: str,
    activity_schedules: List[dict],
    activities: List[dict],
    values: List[dict],
) -> dict:
    # For robustness, authored to allow the "find" to fail when building snapshot

    # Start with an empty snapshot
    activity_schedule = None
    activity = None
    value = None

    # We start with an activity_schedule_id
    if activity_schedule_id:
        activity_schedule = next(
            (
                activity_schedule_current
                for activity_schedule_current in activity_schedules
                if (
                    activity_schedule_current[
                        scope.database.patient.activity_schedules.SEMANTIC_SET_ID
                    ]
                    == activity_schedule_id
                )
            ),
            None
        )

    # Every activity schedule should reference an activity
    if activity_schedule:
        activity_id = activity_schedule.get(scope.database.patient.activities.SEMANTIC_SET_ID, None)
        if activity_id:
            activity = next(
                (
                    activity_current
                    for activity_current in activities
                    if (
                            activity_current[scope.database.patient.activities.SEMANTIC_SET_ID]
                            == activity_id
                    )
                ),
                None
            )

    # An activity may reference a value
    if activity:
        value_id = activity.get(scope.database.patient.values.SEMANTIC_SET_ID, None)
        if value_id:
            value = next(
                (
                    value_current
                    for value_current in values
                    if value_current[scope.database.patient.values.SEMANTIC_SET_ID] == value_id
                ),
                None
            )

    # Build the snapshot
    data_snapshot = {}

    if activity_schedule:
        data_snapshot[scope.database.patient.activity_schedules.DOCUMENT_TYPE] = activity_schedule
    if activity:
        data_snapshot[scope.database.patient.activities.DOCUMENT_TYPE] = activity
    if value:
        data_snapshot[scope.database.patient.values.DOCUMENT_TYPE] = value

    return data_snapshot


def delete_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
    rev: int,
) -> scope.database.collection_utils.SetPutResult:
    """
    Delete "scheduled-activity" document.
    """

    return scope.database.collection_utils.delete_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
        rev=rev,
    )


def get_scheduled_activities(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "scheduledActivity" documents.
    """

    scheduled_activities = scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )

    return scheduled_activities


def get_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "scheduleActivity" document.
    """

    scheduled_activity = scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )

    return scheduled_activity


def maintain_scheduled_activities_data_snapshot(
    *,
    collection: pymongo.collection.Collection,
    maintenance_datetime: datetime.datetime,
) -> List[scope.database.collection_utils.SetPutResult]:
    # Compute pending scheduled activities
    scheduled_activities = get_scheduled_activities(collection=collection)

    # Filter to only maintain those which are pending
    pending_scheduled_activities = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=scheduled_activities,
        after_datetime=maintenance_datetime,
    )

    # TODO: Could further filter for efficiency

    # If there are no pending scheduled activities, we are done
    if not pending_scheduled_activities:
        return []

    # Obtain the documents need to calculate snapshots
    # Do this in 3 queries for the entire collection because that will be faster than many document queries
    activity_schedules = scope.database.patient.get_activity_schedules(
        collection=collection,
    )
    activities = scope.database.patient.get_activities(
        collection=collection,
    )
    values = scope.database.patient.get_values(
        collection=collection,
    )

    # Calculate snapshots and determine which have changed
    scheduled_activities_pending_update = []
    for scheduled_activity_current in pending_scheduled_activities:
        # Capture the existing snapshot
        existing_data_snapshot = scheduled_activity_current.get(
            DATA_SNAPSHOT_PROPERTY, None
        )

        # Calculate a new value for data snapshot
        new_data_snapshot = build_data_snapshot(
            activity_schedule_id=scheduled_activity_current[scope.database.patient.activity_schedules.SEMANTIC_SET_ID],
            activity_schedules=activity_schedules,
            activities=activities,
            values=values,
        )

        # If data snapshot changed, update scheduled activity and add it to pending update list
        if existing_data_snapshot != new_data_snapshot:
            scheduled_activity_current.update(
                {
                    DATA_SNAPSHOT_PROPERTY: new_data_snapshot,
                }
            )
            scheduled_activities_pending_update.append(scheduled_activity_current)

    # Issue the updates for scheduled activities in pending update list
    scheduled_activity_put_results = []
    for scheduled_activity_current in scheduled_activities_pending_update:
        del scheduled_activity_current["_id"]
        scheduled_activity_put_results.append(
            put_scheduled_activity(
                collection=collection,
                set_id=scheduled_activity_current[SEMANTIC_SET_ID],
                scheduled_activity=scheduled_activity_current,
            )
        )

    return scheduled_activity_put_results


def post_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    scheduled_activity: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "scheduleActivity" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=scheduled_activity,
    )


def put_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    scheduled_activity: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "scheduleActivity" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=scheduled_activity,
    )
