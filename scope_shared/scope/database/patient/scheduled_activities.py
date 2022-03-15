import copy
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


# TODO: Anant; Keep the commented code for now.
# def _compute_scheduled_activity_properties(
#     activity: dict, scheduled_activity_due_date: str
# ) -> dict:
#     scheduled_activity = {
#         "_type": DOCUMENT_TYPE,
#         # "dueType": "Exact",
#         "activityId": activity[scope.database.patient.activities.SEMANTIC_SET_ID],
#         "activityName": activity["name"],
#         "timeOfDay": activity["timeOfDay"],
#         "completed": False,
#     }
#     scheduled_activity["dueDate"] = date_utils.format_datetime(
#         date_utils.parse_date(scheduled_activity_due_date)
#         # + datetime.timedelta(hours=activity["timeOfDay"])
#     )
#     if activity.get("hasReminder"):
#         scheduled_activity["reminderTimeOfDay"] = activity["reminderTimeOfDay"]
#
#         # scheduled_activity["reminder"] = date_utils.format_datetime(
#         #     date_utils.parse_date(scheduled_activity_due_date)
#         #     + datetime.timedelta(hours=activity["reminderTimeOfDay"])
#         # )
#     return scheduled_activity


# def create_scheduled_activities(
#     *,
#     activity: dict,
#     weeks: int = 12,
#     activity_method: str,
# ) -> List[dict]:

#     if activity_method == "put":
#         start_date = date_utils.parse_date(activity["startDate"])
#         todays_date = date_utils.parse_date(
#             date_utils.format_date(datetime.date.today())
#         )
#         if start_date < todays_date:
#             activity.update(
#                 {"startDate": date_utils.format_date(datetime.date.today())}
#             )

#     scheduled_activities = []
#     if not activity.get("hasRepetition"):
#         # Create 1 scheduled activity
#         scheduled_activity = _compute_scheduled_activity_properties(
#             activity=activity, scheduled_activity_due_date=activity["startDate"]
#         )
#         scheduled_activities.append(scheduled_activity)
#     else:
#         # Create future dates using startDate and repeatDayFlags for the next 3 months
#         scheduled_activity_due_dates = list(
#             dateutil.rrule.rrule(
#                 dateutil.rrule.WEEKLY,
#                 dtstart=date_utils.parse_date(activity["startDate"]),
#                 until=date_utils.parse_date(activity["startDate"])
#                 + datetime.timedelta(weeks=weeks),
#                 byweekday=_compute_byweekday(
#                     repeat_day_flags=activity["repeatDayFlags"]
#                 ),
#             )
#         )
#         for scheduled_activity_due_date_current in scheduled_activity_due_dates:
#             scheduled_activity = _compute_scheduled_activity_properties(
#                 activity=activity,
#                 scheduled_activity_due_date=date_utils.format_date(
#                     scheduled_activity_due_date_current
#                 ),
#             )
#             scheduled_activities.append(scheduled_activity)

#     return scheduled_activities


# def create_and_post_scheduled_activities(
#     *,
#     collection: pymongo.collection.Collection,
#     activity: dict,
#     weeks: int = 12,  # ~ 3 months
#     activity_method: str,
# ):
#     # Create scheduledActivities here
#     scheduled_activities = create_scheduled_activities(
#         activity=activity,
#         weeks=weeks,
#         activity_method=activity_method,
#     )

#     schema_utils.raise_for_invalid_schema(
#         data=scheduled_activities,
#         schema=scope.schema.scheduled_activities_schema,
#     )

#     for scheduled_activity_current in scheduled_activities:

#         post_scheduled_activity(
#             collection=collection,
#             scheduled_activity=scheduled_activity_current,
#         )


# def filter_scheduled_activities(
#     *,
#     all_scheduled_activities: List[dict],
#     activity: dict,
# ) -> List[dict]:
#     """
#     GET future due date scheduled activities for an activity
#     """

#     if all_scheduled_activities:
#         filtered_scheduled_activities = list(
#             filter(
#                 lambda all_scheduled_activity_current: (
#                     # Keep scheduled activities which match activity
#                     (
#                         all_scheduled_activity_current[
#                             scope.database.patient.activities.SEMANTIC_SET_ID
#                         ]
#                         == activity[scope.database.patient.activities.SEMANTIC_SET_ID]
#                     )
#                     # Keep scheduled activities which are due in future
#                     and (
#                         date_utils.parse_date(all_scheduled_activity_current["dueDate"])
#                         > date_utils.parse_date(
#                             date_utils.format_date(datetime.date.today())
#                         )
#                     )
#                 ),
#                 all_scheduled_activities,
#             )
#         )
#         return filtered_scheduled_activities
#     return []


# def get_filter_and_put_scheduled_activities(
#     *,
#     collection: pymongo.collection.Collection,
#     activity: dict,
# ):

#     # GET all stored scheduledActivities
#     all_scheduled_activities = get_scheduled_activities(
#         collection=collection,
#     )

#     # Get future due date scheduled activities for activity
#     filtered_scheduled_activities = filter_scheduled_activities(
#         all_scheduled_activities=all_scheduled_activities,
#         activity=activity,
#     )

#     schema_utils.raise_for_invalid_schema(
#         data=filtered_scheduled_activities,
#         schema=scope.schema.scheduled_activities_schema,
#     )

#     # PUT the filtered scheduled activities
#     for scheduled_activity_current in filtered_scheduled_activities:
#         # Delete _id for putting
#         del scheduled_activity_current["_id"]
#         # Mark them as deleted
#         scheduled_activity_current.update({"_deleted": True})

#         schema_utils.raise_for_invalid_schema(
#             data=scheduled_activity_current,
#             schema=scope.schema.scheduled_activity_schema,
#         )

#         put_scheduled_activity(
#             collection=collection,
#             scheduled_activity=scheduled_activity_current,
#             set_id=scheduled_activity_current["_set_id"],
#         )


def get_scheduled_activities(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "schedulAactivity" documents.
    """

    scheduled_activities = scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )

    if scheduled_activities:
        scheduled_activities = [
            scheduled_activity_current
            for scheduled_activity_current in scheduled_activities
            if not scheduled_activity_current.get("_deleted", False)
        ]
    return scheduled_activities


def delete_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    scheduled_activity: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    scheduled_activity = copy.deepcopy(scheduled_activity)

    scheduled_activity["_deleted"] = True
    del scheduled_activity["_id"]

    schema_utils.assert_schema(
        data=scheduled_activity,
        schema=scope.schema.scheduled_activity_schema,
    )

    return put_scheduled_activity(
        collection=collection,
        scheduled_activity=scheduled_activity,
        set_id=set_id,
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
