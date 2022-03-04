import datetime
import dateutil.rrule
import dateutil.parser
from typing import List, Optional, Tuple

import pymongo.collection
import scope.database.collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.schema
import scope.schema_utils as schema_utils


DOCUMENT_TYPE = "scheduledActivity"
SEMANTIC_SET_ID = "scheduledActivityId"


def _compute_byweekday(repeat_day_flags: dict) -> Tuple:
    byweekday = []
    for day, day_flag in repeat_day_flags.items():
        if day_flag:
            byweekday.append(date_utils.DATEUTIL_WEEKDAYS_MAP[day])

    return byweekday


def _compute_scheduled_activity_properties(
    activity: dict, scheduled_activity_day_date: str
) -> dict:
    scheduled_activity = {
        "_type": DOCUMENT_TYPE,
        "dueType": "Exact",
        "activityId": activity[scope.database.patient.activities.SEMANTIC_SET_ID],
        "activityName": activity["name"],
        "completed": False,
    }
    scheduled_activity["dueDate"] = date_utils.format_datetime(
        date_utils.parse_date(scheduled_activity_day_date)
        + datetime.timedelta(hours=activity["timeOfDay"])
    )
    if not activity.get("hasReminder"):
        scheduled_activity["reminder"] = None
    else:
        scheduled_activity["reminder"] = date_utils.format_datetime(
            date_utils.parse_date(scheduled_activity_day_date)
            + datetime.timedelta(hours=activity["reminderTimeOfDay"])
        )
    return scheduled_activity


def create_scheduled_activities(
    *,
    activity: dict,
    weeks: int = 12,
) -> List[dict]:
    scheduled_activities = []

    if not activity.get("hasRepetition"):
        # Create 1 scheduled activity
        scheduled_activity = _compute_scheduled_activity_properties(
            activity=activity, scheduled_activity_day_date=activity["startDate"]
        )
        scheduled_activities.append(scheduled_activity)
    else:
        # Create future dates using startDate and repeatDayFlags for the next 3 months
        scheduled_activity_day_dates = list(
            dateutil.rrule.rrule(
                dateutil.rrule.WEEKLY,
                dtstart=date_utils.parse_date(activity["startDate"]),
                until=date_utils.parse_date(activity["startDate"])
                + datetime.timedelta(weeks=weeks),
                byweekday=_compute_byweekday(
                    repeat_day_flags=activity["repeatDayFlags"]
                ),
            )
        )
        for scheduled_activity_day_date_current in scheduled_activity_day_dates:
            scheduled_activity = _compute_scheduled_activity_properties(
                activity=activity,
                scheduled_activity_day_date=date_utils.format_date(
                    scheduled_activity_day_date_current
                ),
            )
            scheduled_activities.append(scheduled_activity)

    schema_utils.raise_for_invalid_schema(
        data=scheduled_activities,
        schema=scope.schema.scheduled_activities_schema,
    )

    return scheduled_activities


def create_and_post_scheduled_activities(
    *,
    collection: pymongo.collection.Collection,
    activity: dict,
    weeks: int = 12,  # ~ 3 months
):
    # Create scheduledActivities here
    scheduled_activities = create_scheduled_activities(
        activity=activity,
        weeks=weeks,
    )
    for scheduled_activity_current in scheduled_activities:
        # TODO: Check w/ James if no return is fine.
        post_scheduled_activity(
            collection=collection,
            scheduled_activity=scheduled_activity_current,
        )


def get_scheduled_activities_for_activity(
    *,
    collection: pymongo.collection.Collection,
    activity_id: str,
) -> Optional[List[dict]]:
    """
    Get list of "schedulAactivity" documents.
    """

    query = {
        "_type": DOCUMENT_TYPE,
        scope.database.patient.activities.SEMANTIC_SET_ID: activity_id,
        # "isDeleted": False, #TODO Check with James
    }

    return scope.database.collection_utils.get_set_query(
        collection=collection,
        match_query=query,
    )


def get_scheduled_activities(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "schedulAactivity" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "scheduleActivity" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


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
