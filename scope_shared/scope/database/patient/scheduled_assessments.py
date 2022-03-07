import copy
import datetime
import dateutil.rrule
import dateutil.parser
import dateutil.relativedelta
from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.assessments
import scope.schema
import scope.schema_utils as schema_utils

DOCUMENT_TYPE = "scheduledAssessment"
SEMANTIC_SET_ID = "scheduledAssessmentId"


def _compute_scheduled_assessments_properties(
    assessment: dict,
    scheduled_assessment_due_dates: List[datetime.datetime],
) -> List[dict]:
    scheduled_assessment_template = {
        "_type": DOCUMENT_TYPE,
        "dueType": "Exact",
        "assessmentId": assessment[scope.database.patient.assessments.SEMANTIC_SET_ID],
        "completed": False,
    }

    scheduled_assessments = []

    for scheduled_assessment_due_date_current in scheduled_assessment_due_dates:

        scheduled_assessment = scheduled_assessment_template.copy()
        scheduled_assessment["dueDate"] = date_utils.format_date(
            scheduled_assessment_due_date_current
        )
        scheduled_assessments.append(scheduled_assessment)

    return scheduled_assessments


def create_scheduled_assessments(
    *,
    assessment: dict,
    weeks: int = 12,
) -> List[dict]:

    # Calculate dueDates
    scheduled_assessments = []
    date_start = date_utils.parse_date(
        date_utils.format_date(
            datetime.date.today()
            + dateutil.relativedelta.relativedelta(
                weekday=date_utils.DATEUTIL_WEEKDAYS_MAP[assessment["dayOfWeek"]]
            )
        )
    )
    until = date_start + datetime.timedelta(weeks=weeks)  # Next 3 months
    if assessment["frequency"] == "Daily":
        scheduled_assessment_due_dates = list(
            dateutil.rrule.rrule(
                dateutil.rrule.DAILY,
                dtstart=date_start,
                until=until,
            )
        )

    elif assessment["frequency"] == "Once a week":
        scheduled_assessment_due_dates = list(
            dateutil.rrule.rrule(
                dateutil.rrule.WEEKLY,
                dtstart=date_start,
                until=until,
                byweekday=(date_utils.DATEUTIL_WEEKDAYS_MAP[assessment["dayOfWeek"]]),
            )
        )
    elif assessment["frequency"] == "Every 2 weeks":
        scheduled_assessment_due_dates = list(
            dateutil.rrule.rrule(
                dateutil.rrule.WEEKLY,
                interval=2,
                dtstart=date_start,
                until=until,
                byweekday=(date_utils.DATEUTIL_WEEKDAYS_MAP[assessment["dayOfWeek"]]),
            )
        )
    elif assessment["frequency"] == "Every 4 weeks":
        scheduled_assessment_due_dates = list(
            dateutil.rrule.rrule(
                dateutil.rrule.WEEKLY,
                interval=4,
                dtstart=date_start,
                until=until,
                byweekday=(date_utils.DATEUTIL_WEEKDAYS_MAP[assessment["dayOfWeek"]]),
            )
        )

    scheduled_assessments = _compute_scheduled_assessments_properties(
        assessment=assessment,
        scheduled_assessment_due_dates=scheduled_assessment_due_dates,
    )

    return scheduled_assessments


def create_and_post_scheduled_assessments(
    *,
    collection: pymongo.collection.Collection,
    assessment: dict,
    weeks: int = 12,  # ~ 3 months
):
    # Create scheduledAssessments here
    scheduled_assessments = create_scheduled_assessments(
        assessment=assessment,
        weeks=weeks,
    )

    schema_utils.raise_for_invalid_schema(
        data=scheduled_assessments,
        schema=scope.schema.scheduled_assessments_schema,
    )

    for scheduled_assessment_current in scheduled_assessments:

        post_scheduled_assessment(
            collection=collection,
            scheduled_assessment=scheduled_assessment_current,
        )


# TODO: Can this method be better named.
def filter_scheduled_assessments(
    *,
    all_scheduled_assessments: List[dict],
    assessment: dict,
) -> List[dict]:
    """
    GET future due date scheduled assessments for an assessment
    """

    if all_scheduled_assessments:
        filtered_scheduled_assessments = list(
            filter(
                lambda all_scheduled_assessment_current: (
                    # Keep scheduled assessments which match assessment
                    (
                        all_scheduled_assessment_current[
                            scope.database.patient.assessments.SEMANTIC_SET_ID
                        ]
                        == assessment[
                            scope.database.patient.assessments.SEMANTIC_SET_ID
                        ]
                    )
                    # Keep scheduled assessments which are due in future
                    and (
                        date_utils.parse_date(
                            all_scheduled_assessment_current["dueDate"]
                        )
                        > date_utils.parse_date(
                            date_utils.format_date(datetime.date.today())
                        )
                    )
                ),
                all_scheduled_assessments,
            )
        )
        return filtered_scheduled_assessments
    return []


def get_filter_and_put_scheduled_assessments(
    *,
    collection: pymongo.collection.Collection,
    assessment: dict,
):

    # GET all stored scheduledAssessments
    all_scheduled_assessments = get_scheduled_assessments(
        collection=collection,
    )

    # Get future due date scheduled assessments for assessment
    filtered_scheduled_assessments = filter_scheduled_assessments(
        all_scheduled_assessments=all_scheduled_assessments,
        assessment=assessment,
    )

    schema_utils.raise_for_invalid_schema(
        data=filtered_scheduled_assessments,
        schema=scope.schema.scheduled_assessments_schema,
    )

    # PUT the filtered scheduled assessments
    for scheduled_assessment_current in filtered_scheduled_assessments:
        # Delete _id for putting
        del scheduled_assessment_current["_id"]

        # Mark them as deleted
        scheduled_assessment_current.update({"_deleted": True})

        schema_utils.raise_for_invalid_schema(
            data=scheduled_assessment_current,
            schema=scope.schema.scheduled_assessment_schema,
        )

        put_scheduled_assessment(
            collection=collection,
            scheduled_assessment=scheduled_assessment_current,
            set_id=scheduled_assessment_current["_set_id"],
        )


def get_scheduled_assessments(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "scheduleAssessment" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "scheduleAssessment" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    scheduled_assessment: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "scheduleAssessment" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=scheduled_assessment,
    )


def put_scheduled_assessment(
    *,
    collection: pymongo.collection.Collection,
    scheduled_assessment: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "scheduleAssessment" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=scheduled_assessment,
    )
