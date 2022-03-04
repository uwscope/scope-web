import copy
import datetime
from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.scheduled_activities

DOCUMENT_TYPE = "activity"
SEMANTIC_SET_ID = "activityId"


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
    scope.database.patient.scheduled_activities.create_and_post_scheduled_activities(
        collection=collection,
        activity=activity_set_post_result.document,
        weeks=12,  # ~ 3 months
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

    # GET already stored scheduledActivities for this activity
    stored_scheduled_activities = scope.database.patient.scheduled_activities.get_scheduled_activities_for_activity(
        collection=collection,
        activity_id=activity,
    )

    # Update the stored scheduled activities
    for stored_scheduled_activity_current in stored_scheduled_activities:
        # TODO: Check w/ James if no return is fine.
        del stored_scheduled_activity_current["_id"]
        due_date = date_utils.parse_datetime(
            stored_scheduled_activity_current["dueDate"]
        )
        if due_date > datetime.datetime.today():
            # Mark the future scheduled activities as deleted
            stored_scheduled_activity_current.update({"isDeleted": True})
            scope.database.patient.scheduled_activities.put_scheduled_activity(
                collection=collection,
                scheduled_activity=stored_scheduled_activity_current,
                set_id=stored_scheduled_activity_current["_set_id"],
            )

    # Update start date of activity to create scheduled activities
    # TODO: Find better name than activity_copy
    activity_copy = copy.deepcopy(activity)
    start_date = date_utils.parse_date(activity_copy["startDate"])
    if start_date < datetime.datetime.today().date():
        activity_copy.update(
            {"startDate": date_utils.format_date(datetime.datetime.today())}
        )

    # Create and post scheduled activities.
    scope.database.patient.scheduled_activities.create_and_post_scheduled_activities(
        collection=collection,
        activity=activity_copy,
        weeks=12,  # ~ 3 months
    )

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=activity,
    )
