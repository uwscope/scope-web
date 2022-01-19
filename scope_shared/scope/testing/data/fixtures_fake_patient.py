import random
from datetime import date, datetime, timedelta
from typing import Callable, List

import bson.json_util
import bson.objectid
import numpy as np
import pytest
from lorem.text import TextLorem

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

    # 10 assessments in the past and 10 in the future
    scheduled = []
    for idx in list(range(-10, 10)):
        scheduled.append(
            {
                "scheduleId": "Scheduled {}".format(idx),
                "assessmentId": assessment["_assessment_id"],
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


def _fake_name_factory() -> str:
    first_names = [
        "Paisley",
        "Vince",
        "Prudence",
        "Floyd",
        "Marty",
        "Yvonne",
        "Russ",
        "Herb",
        "Hannah",
        "Melanie",
        "Dwayne",
        "Clifford",
        "Garth",
        "Rachel",
        "Phoebe",
        "Doug",
        "Mortimer",
        "Heath",
        "Iris",
        "Tony",
    ]

    last_names = [
        "Lowe",
        "Dawson",
        "Porter",
        "Tomlinson",
        "Windrow",
        "Cook",
        "Wolfe",
        "Chapman",
        "Malone",
        "Green",
        "Fairbank",
        "Wood",
        "Miller",
        "Clayton",
        "Russell",
        "Atkinson",
        "Whitehead",
        "Greene",
        "Cannon",
        "Pope",
    ]

    return "{} {}".format(random.choice(first_names), random.choice(last_names))


def data_fake_identity_factory() -> dict:
    fake_identity = {
        # "_id": str(bson.objectid.ObjectId()),
        "_type": "identity",
        "_rev": 1,
        "name": _fake_name_factory(),
    }

    # TODO: Verify the schema

    return fake_identity


def data_fake_patient_profile_factory() -> dict:

    name = _fake_name_factory()
    mrn = "%s" % get_random_integer(10000, 1000000)

    fake_profile = {
        "_type": "patientProfile",
        "_rev": 1,
        "name": name,
        "MRN": mrn,
        "clinicCode": get_random_item(ClinicCode).value,
        "birthdate": str(
            datetime(
                get_random_integer(1930, 2000),
                get_random_integer(1, 13),
                get_random_integer(1, 28),
            )
        ),
        "sex": get_random_item(PatientSex).value,
        "gender": get_random_item(PatientGender).value,
        "pronoun": get_random_item(PatientPronoun).value,
        "race": get_random_flags(PatientRace),
        "primaryOncologyProvider": data_fake_identity_factory(),
        "primaryCareManager": data_fake_identity_factory(),
        "discussionFlag": get_random_flags(DiscussionFlag),
        "followupSchedule": get_random_item(FollowupSchedule).value,
        "depressionTreatmentStatus": get_random_item(DepressionTreatmentStatus).value,
    }

    # TODO: Verify the schema

    return fake_profile


def data_fake_clinical_history_factory() -> dict:
    fake_clinical_history = {
        # "_id": str(bson.objectid.ObjectId()),
        "_type": "clinicalHistory",
        "_rev": 1,
        "primaryCancerDiagnosis": "primaryCancerDiagnosis",
        "dateOfCancerDiagnosis": "dateOfCancerDiagnosis",  # TODO: date pattern needs to be fixed in schema
        "currentTreatmentRegimen": {
            "Surgery": True,
            "Chemotherapy": True,
            "Radiation": True,
            "Stem Cell Transplant": True,
            "Immunotherapy": True,
            "CAR-T": True,
            "Endocrine": True,
            "Surveillance": True,
        },
        "currentTreatmentRegimenOther": "currentTreatmentRegimenOther",
        "currentTreatmentRegimenNotes": "currentTreatmentRegimenNotes",
        "psychDiagnosis": "psychDiagnosis",
        "pastPsychHistory": "pastPsychHistory",
        "pastSubstanceUse": "pastSubstanceUse",
        "psychSocialBackground": "psychSocialBackground",
    }

    # TODO: Verify the schema

    return fake_clinical_history


def data_fake_values_inventory_factory() -> dict:
    fake_values_inventory = {
        # "_id": str(bson.objectid.ObjectId()),
        "_type": "valuesInventory",
        "_rev": 1,
        "assigned": True,
        "assignedDate": "assignedDate",  # TODO: date pattern needs to be fixed in schema
        "values": [
            {
                "id": "id",
                "name": "name",
                "dateCreated": "",
                "dateEdited": "",
                "lifeareaId": "",
                "activities": [
                    {
                        "id": "id",
                        "name": "name",
                        "valueId": "",
                        "dateCreated": "",
                        "dateEdited": "",
                        "lifeareaId": "",
                    },
                    {
                        "id": "id",
                        "name": "name",
                        "valueId": "",
                        "dateCreated": "",
                        "dateEdited": "",
                        "lifeareaId": "",
                    },
                ],
            }
        ],
    }

    # TODO: Verify the schema

    return fake_values_inventory


def data_fake_safety_plan_factory() -> dict:
    fake_safety_plan = {
        "_type": "safetyPlan",
        "_rev": 1,
        "assigned": True,
        "assignedDate": "some date",
        "reasonsForLiving": "To stare at Mt. Rainier.",
        "supporters": [
            {
                "contactType": "Person",
                "name": "Name",
                "address": "Address",
                "phoneNumber": "Number",
            }
        ],
    }

    # TODO: Verify the schema

    return fake_safety_plan


def data_fake_sessions_factory() -> List[dict]:
    session_count = get_random_integer(1, 10)
    random_referrals = get_random_states(Referral, ReferralStatus)
    referrals = []
    for referral in random_referrals:
        if random_referrals[referral] != "Not Referred":
            referrals.append(
                {"referralType": referral, "referralStatus": random_referrals[referral]}
            )

    fake_sessions = [
        {
            "_session_id": "Initial assessment" if idx == 0 else "session-%d" % idx,
            "_type": "session",
            "_rev": 1,
            "date": str(
                datetime.now()
                - timedelta(
                    days=get_random_integer(-2, 2)
                    + (session_count - idx) * get_random_integer(13, 18)
                )
            ),
            "sessionType": get_random_item(SessionType).value,
            "billableMinutes": int(get_random_item([30, 45, 60, 80])),
            "medicationChange": shortLorem.sentence() if get_random_boolean() else "",
            "currentMedications": shortLorem.sentence() if get_random_boolean() else "",
            "behavioralStrategyChecklist": get_random_flags(
                BehavioralStrategyChecklist
            ),
            "behavioralStrategyOther": shortLorem.sentence()
            if get_random_boolean()
            else "",
            "behavioralActivationChecklist": get_random_flags(
                BehavioralActivationChecklist
            ),
            "referrals": referrals,
            "otherRecommendations": shortLorem.sentence(),
            "sessionNote": lorem.paragraph(),
        }
        for idx in range(session_count)
    ]
    # TODO: Verify the schema

    return fake_sessions


def data_fake_session_factory() -> dict:
    idx = get_random_integer(1, 10)
    random_referrals = get_random_states(Referral, ReferralStatus)
    referrals = []
    for referral in random_referrals:
        if random_referrals[referral] != "Not Referred":
            referrals.append(
                {"referralType": referral, "referralStatus": random_referrals[referral]}
            )

    fake_session = {
        "_session_id": "session-%d" % idx,
        "_type": "session",
        "_rev": 1,
        "date": str(
            datetime.now()
            - timedelta(days=get_random_integer(-2, 2) + get_random_integer(13, 18))
        ),
        "sessionType": get_random_item(SessionType).value,
        "billableMinutes": int(get_random_item([30, 45, 60, 80])),
        "medicationChange": shortLorem.sentence() if get_random_boolean() else "",
        "currentMedications": shortLorem.sentence() if get_random_boolean() else "",
        "behavioralStrategyChecklist": get_random_flags(BehavioralStrategyChecklist),
        "behavioralStrategyOther": shortLorem.sentence()
        if get_random_boolean()
        else "",
        "behavioralActivationChecklist": get_random_flags(
            BehavioralActivationChecklist
        ),
        "referrals": referrals,
        "otherRecommendations": shortLorem.sentence(),
        "sessionNote": lorem.paragraph(),
    }

    # TODO: Verify the schema

    return fake_session


def data_fake_case_reviews_factory() -> List[dict]:
    case_review_count = get_random_integer(1, 10)

    fake_case_reviews = [
        {
            "_review_id": "Initial review" if idx == 0 else "review-%d" % idx,
            "_type": "caseReview",
            "_rev": 1,
            "date": str(
                datetime.now()
                - timedelta(
                    days=get_random_integer(-2, 2)
                    + (case_review_count - idx) * get_random_integer(13, 18)
                )
            ),
            "consultingPsychiatrist": data_fake_identity_factory(),
            "medicationChange": shortLorem.sentence(),
            "behavioralStrategyChange": shortLorem.sentence(),
            "referralsChange": shortLorem.sentence(),
            "otherRecommendations": shortLorem.sentence(),
            "reviewNote": lorem.paragraph(),
        }
        for idx in range(case_review_count)
    ]
    # TODO: Verify the schema

    return fake_case_reviews


def data_fake_case_review_factory() -> dict:
    idx = get_random_integer(1, 10)
    fake_case_review = {
        "_review_id": "review-%d" % idx,
        "_type": "caseReview",
        "_rev": 1,
        "date": str(
            datetime.now()
            - timedelta(days=get_random_integer(-2, 2) + get_random_integer(13, 18))
        ),
        "consultingPsychiatrist": data_fake_identity_factory(),
        "medicationChange": shortLorem.sentence(),
        "behavioralStrategyChange": shortLorem.sentence(),
        "referralsChange": shortLorem.sentence(),
        "otherRecommendations": shortLorem.sentence(),
        "reviewNote": lorem.paragraph(),
    }

    # TODO: Verify the schema

    return fake_case_review


def data_fake_assessments_factory() -> List[dict]:
    return get_fake_assessments()


def data_fake_patient_factory() -> dict:
    fake_patient = {
        # NOTE: A "patient" exists only as a query composed from other documents.
        # Because a "patient" is never stored to the database, it will not have an "_id".
        # Below `_id` isn't being used anywhere for now except in James' version of CRUD patients code.
        # "_id": str(bson.objectid.ObjectId()),
        "_type": "patient",
        "identity": data_fake_identity_factory(),
        "patientProfile": data_fake_patient_profile_factory(),
        "clinicalHistory": data_fake_clinical_history_factory(),  # NOTE: In typescipt, all the keys in clinicalHistory are optional. Chat with James about this.
        "valuesInventory": data_fake_values_inventory_factory(),
        "safetyPlan": data_fake_safety_plan_factory(),
        "sessions": data_fake_sessions_factory(),
        "caseReviews": data_fake_case_reviews_factory(),
        "assessments": data_fake_assessments_factory(),
        "assessmentLogs": data_fake_assessment_logs_factory(),
    }

    # TODO: Verify the schema

    return fake_patient


@pytest.fixture(name="data_fake_patient_factory")
def fixture_data_fake_patient_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_patient_factory.

    Provides a factory for obtaining data for a fake patient.
    """

    return data_fake_patient_factory


@pytest.fixture(name="data_fake_patient_profile_factory")
def fixture_data_fake_profile_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_patient_profile_factory.

    Provides a factory for obtaining data for a fake profile.
    """

    return data_fake_patient_profile_factory


@pytest.fixture(name="data_fake_clinical_history_factory")
def fixture_data_fake_clinical_history_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_clinical_history_factory.

    Provides a factory for obtaining data for a fake clinical history.
    """

    return data_fake_clinical_history_factory


@pytest.fixture(name="data_fake_values_inventory_factory")
def fixture_data_fake_values_inventory_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_values_inventory_factory.

    Provides a factory for obtaining data for a fake values inventory.
    """

    return data_fake_values_inventory_factory


@pytest.fixture(name="data_fake_safety_plan_factory")
def fixture_data_fake_safety_plan_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_safety_plan_factory.

    Provides a factory for obtaining data for a fake safety plan.
    """

    return data_fake_safety_plan_factory


@pytest.fixture(name="data_fake_sessions_factory")
def fixture_data_fake_sessions_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_sessions_factory.

    Provides a factory for obtaining data for a list of sessions.
    """

    return data_fake_sessions_factory


@pytest.fixture(name="data_fake_session_factory")
def fixture_data_fake_session_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_session_factory.

    Provides a factory for obtaining data for a session.
    """

    return data_fake_session_factory


@pytest.fixture(name="data_fake_case_reviews_factory")
def fixture_data_fake_case_reviews_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_case_reviews_factory.

    Provides a factory for obtaining data for a list of case reviews.
    """

    return data_fake_case_reviews_factory


@pytest.fixture(name="data_fake_case_review_factory")
def fixture_data_fake_case_review_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_case_review_factory.

    Provides a factory for obtaining data for a case review.
    """

    return data_fake_case_review_factory
