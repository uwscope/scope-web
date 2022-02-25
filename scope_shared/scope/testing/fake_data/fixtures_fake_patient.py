import random
from datetime import date, datetime, timedelta
from typing import Callable, List

import bson.json_util
import bson.objectid
import numpy as np
import pytest
from jschon import JSON
from lorem.text import TextLorem
from scope.schema import (
    activities_schema,
    activity_logs_schema,
    assessment_logs_schema,
    assessments_schema,
    case_review_schema,
    case_reviews_schema,
    clinical_history_schema,
    identity_schema,
    mood_logs_schema,
    patient_profile_schema,
    patient_schema,
    safety_plan_schema,
    scheduled_activities_schema,
    scheduled_assessments_schema,
    session_schema,
    sessions_schema,
    values_inventory_schema,
)

from .assessments import *
from .enums import *

lorem = TextLorem(srange=(4, 16), prange=(4, 8))
shortLorem = TextLorem(srange=(4, 8), prange=(1, 3))


def get_random_integer(min_inclusive, max_exclusive):
    return int(np.random.randint(low=min_inclusive, high=max_exclusive))


def get_random_item(enum):
    return np.random.choice(enum, 1)[0]


def get_random_boolean():
    return np.random.randint(0, 2) == 0


def sample(enum, count):
    return np.random.choice(enum, count, replace=False)


def get_random_flags(enum):
    flags = dict()
    for key in enum:
        flags[key.value] = get_random_boolean()

    return flags


def get_random_states(enum, options):
    flags = dict()
    for key in enum:
        flags[key.value] = get_random_item(options).value

    return flags


def get_fake_assessments():
    return [
        {
            "assessmentId": "mood"
            if a.value == "Mood Logging"
            else "medication"
            if a.value == "Medication Tracking"
            else a.value.lower(),
            "assessmentName": a.value,
            "frequency": get_random_item(AssessmentFrequency).value,
            "dayOfWeek": get_random_item(DayOfWeek).value,
        }
        for a in AssessmentType
    ]


def get_fake_scheduled_assessment(assessment):

    if assessment["assessmentId"] == "mood":
        return []

    freq = 0
    if assessment["frequency"] == "Daily":
        freq = 1
    elif assessment["frequency"] == "Once a week":
        freq = 7
    elif assessment["frequency"] == "Every 2 weeks":
        freq = 14
    elif assessment["frequency"] == "Monthly":
        freq = 28

    dow = 0
    dowValues = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    for idx in range(len(dowValues)):
        if assessment["dayOfWeek"] == dowValues[idx]:
            dow = idx
            break

    dueDate = datetime.today() + timedelta(days=7 - date.today().weekday() + dow)

    # 10 assessments in the past and 10 in the future
    scheduled = []
    for idx in list(range(-10, 10)):
        scheduled.append(
            {
                "scheduleId": "Scheduled {}".format(idx),
                "assessmentId": assessment["assessmentId"],
                "assessmentName": assessment["assessmentName"],
                "dueDate": dueDate + timedelta(days=freq * idx),
            }
        )

    return scheduled


def get_fake_assessment_data_point(assessmentType):
    points = dict()
    if assessmentType == "PHQ-9":
        for q in phq9Assessment.get("questions", []):
            points[q["id"]] = get_random_integer(0, 4)
        return points
    elif assessmentType == "GAD-7":
        for q in gad7Assessment.get("questions", []):
            points[q["id"]] = get_random_integer(0, 4)
        return points
    elif assessmentType == "Mood Logging":
        return {"Mood": get_random_integer(1, 11)}
    elif assessmentType == "Medication Tracking":
        return {"Adherence": get_random_integer(1, 6)}
    else:
        return {}


def get_fake_assessment_data_points(assessment_type):
    if assessment_type == "Mood Logging":
        return [
            {
                "assessmentDataId": "%s-%d" % (assessment_type, idx),
                "assessmentType": assessment_type,
                "date": datetime.now()
                - timedelta(
                    hours=get_random_integer(4, 48) + idx * get_random_integer(0, 120)
                ),
                "pointValues": get_fake_assessment_data_point(assessment_type),
                "comment": shortLorem.paragraph(),
                "patientSubmitted": get_random_boolean(),
            }
            for idx in range(get_random_integer(5, 10))
        ]
    else:
        data = [
            {
                "assessmentDataId": "%s-%d" % (assessment_type, idx),
                "assessmentType": assessment_type,
                "date": datetime.now()
                + timedelta(days=14)
                - timedelta(
                    days=get_random_integer(0, 3) + idx * get_random_integer(5, 8)
                ),
                "pointValues": get_fake_assessment_data_point(assessment_type),
                "comment": shortLorem.paragraph(),
                "patientSubmitted": get_random_boolean(),
            }
            for idx in range(get_random_integer(5, 10))
        ]

        for d in data:
            if d["date"] > datetime.now():
                d["pointValues"] = None
                d["comment"] = None
                d["patientSubmitted"] = None

        return data


def data_fake_assessment_logs_factory() -> List[dict]:

    assessments = get_fake_assessments()
    scheduled_assessments_list = [get_fake_scheduled_assessment(a) for a in assessments]
    scheduled_assessments = [
        a for scheduled_list in scheduled_assessments_list for a in scheduled_list
    ]

    assessment_logs = [
        {
            "_log_id": a["scheduleId"] + "_logged",
            "_type": "assessmentLog",
            "_rev": 1,
            "recordedDate": str(
                a["dueDate"] + timedelta(days=get_random_integer(-1, 2))
            ),
            "comment": shortLorem.paragraph(),
            "scheduleId": a["scheduleId"],
            "assessmentId": a["assessmentId"],
            "assessmentName": a["assessmentName"],
            "completed": get_random_boolean(),
            "patientSubmitted": get_random_boolean(),
            "submittedBy": data_fake_identity_factory(),
            # "submittedBy": "Auto generated",
            "pointValues": get_fake_assessment_data_point(a["assessmentName"]),
            # "totalScore": None,
            "totalScore": get_random_integer(0, 100),
        }
        for a in scheduled_assessments
        if a["dueDate"] < datetime.today()
    ]

    return assessment_logs


def get_fake_assessments():
    return [
        {
            # "assessmentId": "mood"
            "_assessment_id": "mood"
            if a.value == "Mood Logging"
            else "medication"
            if a.value == "Medication Tracking"
            else a.value.lower(),
            "_type": "assessment",
            "_rev": 1,
            "assessmentName": a.value,
            "frequency": get_random_item(AssessmentFrequency).value,
            "dayOfWeek": get_random_item(DayOfWeek).value,
        }
        for a in AssessmentType
    ]


def get_fake_scheduled_assessment(assessment):

    if assessment["_assessment_id"] == "mood":
        return []

    freq = 0
    if assessment["frequency"] == "Daily":
        freq = 1
    elif assessment["frequency"] == "Once a week":
        freq = 7
    elif assessment["frequency"] == "Every 2 weeks":
        freq = 14
    elif assessment["frequency"] == "Monthly":
        freq = 28

    dow = 0
    dowValues = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    for idx in range(len(dowValues)):
        if assessment["dayOfWeek"] == dowValues[idx]:
            dow = idx
            break

    dueDate = datetime.today() + timedelta(days=7 - date.today().weekday() + dow)

    # 10 assessments in the past and 10 in the future.
    # NOTE: Anant changed these to 5 in the past and 5 in the future.
    scheduled = []
    for idx in list(range(-5, 5)):
        scheduled.append(
            {
                # "scheduleId": "Scheduled %d" % idx, # NOTE: Wasn't unique, appended _assessment_id to make it unique.
                "_schedule_id": "Scheduled-Assessment-{}-{}".format(
                    idx, assessment["_assessment_id"]
                ),
                "_type": "scheduledAssessment",
                "_rev": 1,
                "assessmentId": assessment["_assessment_id"],
                "assessmentName": assessment["assessmentName"],
                "dueDate": str(dueDate + timedelta(days=freq * idx)),
            }
        )

    return scheduled


def get_fake_assessment_data_point(assessmentType):
    points = dict()
    if assessmentType == "PHQ-9":
        for q in phq9Assessment.get("questions", []):
            points[q["id"]] = get_random_integer(0, 4)
        return points
    elif assessmentType == "GAD-7":
        for q in gad7Assessment.get("questions", []):
            points[q["id"]] = get_random_integer(0, 4)
        return points
    elif assessmentType == "Mood Logging":
        return {"Mood": get_random_integer(1, 11)}
    elif assessmentType == "Medication Tracking":
        return {"Adherence": get_random_integer(1, 6)}
    else:
        return {}


def get_fake_assessment_data_points(assessment_type):
    if assessment_type == "Mood Logging":
        return [
            {
                "assessmentDataId": "%s-%d" % (assessment_type, idx),
                "assessmentType": assessment_type,
                "date": datetime.now()
                - timedelta(
                    hours=get_random_integer(4, 48) + idx * get_random_integer(0, 120)
                ),
                "pointValues": get_fake_assessment_data_point(assessment_type),
                "comment": shortLorem.paragraph(),
                "patientSubmitted": get_random_boolean(),
            }
            for idx in range(get_random_integer(5, 10))
        ]
    else:
        data = [
            {
                "assessmentDataId": "%s-%d" % (assessment_type, idx),
                "assessmentType": assessment_type,
                "date": datetime.now()
                + timedelta(days=14)
                - timedelta(
                    days=get_random_integer(0, 3) + idx * get_random_integer(5, 8)
                ),
                "pointValues": get_fake_assessment_data_point(assessment_type),
                "comment": shortLorem.paragraph(),
                "patientSubmitted": get_random_boolean(),
            }
            for idx in range(get_random_integer(5, 10))
        ]

        for d in data:
            if d["date"] > datetime.now():
                d["pointValues"] = None
                d["comment"] = None
                d["patientSubmitted"] = None

        return data


def data_fake_assessments_factory() -> List[dict]:
    fake_assessments = get_fake_assessments()

    # Verify the schema
    result = assessments_schema.evaluate(JSON(fake_assessments))
    assert result.output("basic")["valid"] == True

    return fake_assessments


def data_fake_scheduled_assessments_factory() -> List[dict]:
    assessments = get_fake_assessments()
    scheduled_assessments_list = [get_fake_scheduled_assessment(a) for a in assessments]
    scheduled_assessments = [
        a for scheduled_list in scheduled_assessments_list for a in scheduled_list
    ]

    # Verify the schema
    result = scheduled_assessments_schema.evaluate(JSON(scheduled_assessments))
    assert result.output("basic")["valid"] == True
    return scheduled_assessments


def data_fake_assessment_logs_factory() -> List[dict]:

    scheduled_assessments = data_fake_scheduled_assessments_factory()

    assessment_logs = [
        {
            # "logId": a["scheduleId"] + "_logged",
            "_log_id": a["_schedule_id"] + "-logged",
            "_type": "assessmentLog",
            "_rev": 1,
            "recordedDate": a["dueDate"],
            "comment": shortLorem.paragraph(),
            "scheduleId": a["_schedule_id"],
            "assessmentId": a["assessmentId"],
            "assessmentName": a["assessmentName"],
            "completed": get_random_boolean(),
            "patientSubmitted": get_random_boolean(),
            "submittedBy": data_fake_identity_factory(),
            # "submittedBy": "Auto generated",
            "pointValues": get_fake_assessment_data_point(a["assessmentName"]),
            # "totalScore": None,
            "totalScore": get_random_integer(0, 100),
        }
        for a in random.sample(
            scheduled_assessments, 5
        )  # Sample 5 scheduled assessments.
        # if a["dueDate"] < datetime.today()
    ]

    # Verify the schema
    result = assessment_logs_schema.evaluate(JSON(assessment_logs))
    assert result.output("basic")["valid"] == True

    return assessment_logs


def data_fake_scheduled_activities_factory() -> List[dict]:
    activities = data_fake_activities_factory()
    fake_scheduled_activities = [
        {
            "_schedule_id": "Scheduled-Activity-{}".format(activity["_activity_id"]),
            "_type": "scheduledActivity",
            "_rev": 1,
            "dueDate": str(
                datetime(
                    get_random_integer(1930, 2000),
                    get_random_integer(1, 13),
                    get_random_integer(1, 28),
                )
            ),
            "dueType": get_random_item(DueType).value,
            "activityId": activity["_activity_id"],
            "activityName": activity["name"],
            "reminder": str(
                datetime(
                    get_random_integer(1930, 2000),
                    get_random_integer(1, 13),
                    get_random_integer(1, 28),
                )
            ),
            "completed": get_random_boolean(),
        }
        for activity in activities
    ]

    # Verify the schema
    result = scheduled_activities_schema.evaluate(JSON(fake_scheduled_activities))
    assert result.output("basic")["valid"] == True

    return fake_scheduled_activities


def data_fake_activity_logs_factory() -> List[dict]:
    scheduled_activities = data_fake_scheduled_activities_factory()
    fake_activity_logs = [
        {
            "_log_id": sa["_schedule_id"] + "-logged",
            "_type": "activityLog",
            "_rev": 1,
            "recordedDate": sa["dueDate"],
            "comment": shortLorem.paragraph(),
            "scheduleId": sa["_schedule_id"],
            "activityName": sa["activityName"],
            "completed": get_random_boolean(),
        }
        for sa in scheduled_activities
    ]
    # Verify the schema
    result = activity_logs_schema.evaluate(JSON(fake_activity_logs))
    assert result.output("basic")["valid"] == True

    return fake_activity_logs


def data_fake_mood_logs_factory() -> List[dict]:
    fake_mood_logs = [
        {
            "_log_id": "mood_%d_logged" % idx,
            "_type": "moodLog",
            "_rev": 1,
            "recordedDate": str(
                datetime.today()
                + timedelta(
                    days=-get_random_integer(0, 40), hours=get_random_integer(0, 24)
                )
            ),
            "comment": shortLorem.paragraph(),
            "mood": get_random_integer(1, 11),
        }
        for idx in range(0, get_random_integer(1, 5))
    ]
    # Verify the schema
    result = mood_logs_schema.evaluate(JSON(fake_mood_logs))
    assert result.output("basic")["valid"] == True

    return fake_mood_logs


def data_fake_patient_factory() -> dict:
    fake_patient = {
        # NOTE: A "patient" exists only as a query composed from other documents.
        # Because a "patient" is never stored to the database, it will not have an "_id".
        # Below `_id` isn't being used anywhere for now except in James' version of CRUD patients code.
        # "_id": str(bson.objectid.ObjectId()),
        "_type": "patient",
        "identity": data_fake_identity_factory(),
        # Patient info
        "profile": data_fake_patient_profile_factory(),
        "clinicalHistory": data_fake_clinical_history_factory(),  # NOTE: In typescipt, all the keys in clinicalHistory are optional. Chat with James about this.
        # Values inventory and safety plan
        "valuesInventory": data_fake_values_inventory_factory(),
        "safetyPlan": data_fake_safety_plan_factory(),
        # Sessions
        "sessions": data_fake_sessions_factory(),
        "caseReviews": data_fake_case_reviews_factory(),
        # Assessments
        "assessments": data_fake_assessments_factory(),
        "scheduledAssessments": data_fake_scheduled_assessments_factory(),
        "assessmentLogs": data_fake_assessment_logs_factory(),  # NOTE: Taking too much time in insert_many operation.
        # Activities
        "activities": data_fake_activities_factory(),
        "scheduledActivities": data_fake_scheduled_activities_factory(),
        "activityLogs": data_fake_activity_logs_factory(),
        # Mood logs
        "moodLogs": data_fake_mood_logs_factory(),
    }

    # Verify the schema
    result = patient_schema.evaluate(JSON(fake_patient))
    assert result.output("basic")["valid"] == True
    return fake_patient


@pytest.fixture(name="data_fake_patient_factory")
def fixture_data_fake_patient_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_patient_factory.

    Provides a factory for obtaining data for a fake patient.
    """

    return data_fake_patient_factory
