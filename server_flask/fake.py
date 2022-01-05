import uuid
from datetime import date, datetime, timedelta

import numpy as np
from lorem.text import TextLorem

from assessments import gad7Assessment, moodAssessment, phq9Assessment
from enums import (AssessmentFrequency, AssessmentType,
                   BehavioralActivationChecklist, BehavioralStrategyChecklist,
                   CancerTreatmentRegimen, ClinicCode, DayOfWeek,
                   DepressionTreatmentStatus, DiscussionFlag, FollowupSchedule,
                   PatientGender, PatientPronoun, PatientRaceEthnicity,
                   PatientSex, Referral, ReferralStatus, SessionType,
                   TreatmentChange, TreatmentPlan)

lorem = TextLorem(srange=(4, 16), prange=(4, 8))
shortLorem = TextLorem(srange=(4, 8), prange=(1, 3))

firstNames = [
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

lastNames = [
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

careManagers = ["Luke Skywalker", "Leia Organa", "Han Solo", "Padme Amidala"]
oncologyProviders = ["Darth Vader", "Chewbacca", "R2-D2", "Obi-Wan Kenobi"]


def getRandomFakePatients():
    return [getFakePatient() for idx in range(getRandomInteger(10, 15))]



def getFakePatient():
    recordId = str(uuid.uuid1())
    name = "%s %s" % (getRandomItem(firstNames), getRandomItem(lastNames))
    mrn = "%s" % getRandomInteger(10000, 1000000)

    assessments = getFakeAssessments()

    scheduledAssessmentsList = [getFakeScheduledAssessment(a) for a in assessments]
    scheduledAssessments = [a for scheduledList in scheduledAssessmentsList for a in scheduledList]
    loggedAssessments = [{
        "logId": a["scheduleId"] + "_logged",
        "recordedDate": a["dueDate"] + timedelta(days=getRandomInteger(-1, 2)),
        "comment": shortLorem.paragraph(),
        "scheduleId": a["scheduleId"],
        "assessmentId": a["assessmentId"],
        "assessmentName": a["assessmentName"],
        "completed": getRandomBoolean(),
        "patientSubmitted": getRandomBoolean(),
        "submittedBy": "Auto generated",
        "pointValues": getFakeAssessmentDataPoint(a["assessmentName"]),
        "totalScore": None,
    } for a in scheduledAssessments if a["dueDate"] < datetime.today()]

    loggedMood = [{
        "logId": "mood_%d_logged" % idx,
        "recordedDate": datetime.today() + timedelta(days=-getRandomInteger(0, 40), hours=getRandomInteger(0, 24)),
        "comment": shortLorem.paragraph(),
        "mood": getRandomInteger(1, 11)
    } for idx in range(0, getRandomInteger(1, 40)) ]

    return {
        "identity": {
            "identityId": recordId,
            "name": name
        },

        "profile": {
            "name": name,
            "MRN": mrn,
            "clinicCode": getRandomItem(ClinicCode).value,
            "birthdate": datetime(
                getRandomInteger(1930, 2000),
                getRandomInteger(1, 13),
                getRandomInteger(1, 28),
            ),
            "sex": getRandomItem(PatientSex).value,
            "gender": getRandomItem(PatientGender).value,
            "pronoun": getRandomItem(PatientPronoun).value,
            "race": getRandomItem(PatientRaceEthnicity).value,
            "primaryOncologyProvider": {
                "identityId": str(uuid.uuid1()),
                "name": getRandomItem(oncologyProviders)
            },
            "primaryCareManager": {
                "identityId": str(uuid.uuid1()),
                "name": getRandomItem(careManagers)
            },
            "discussionFlag": getRandomFlags(DiscussionFlag),
            "followupSchedule": getRandomItem(FollowupSchedule).value,
            "depressionTreatmentStatus": getRandomItem(DepressionTreatmentStatus).value,
        },
        "clinicalHistory": {
            "primaryCancerDiagnosis": shortLorem.paragraph(),
            "dateOfCancerDiagnosis": datetime(
                getRandomInteger(2000, 2021),
                getRandomInteger(1, 12),
                getRandomInteger(1, 28),
            ).strftime("%m/%d/%Y"),
            "currentTreatmentRegimen": getRandomFlags(CancerTreatmentRegimen),
            "currentTreatmentRegimenOther": shortLorem.sentence(),
            "currentTreatmentRegimenNotes": shortLorem.sentence(),
            "psychDiagnosis": shortLorem.paragraph(),
            "pastPsychHistory": shortLorem.paragraph(),
            "pastSubstanceUse": shortLorem.paragraph(),
            "psychSocialBackground": shortLorem.paragraph(),
        },

        # Sessions
        "sessions": getFakeSessions(),

        # Assessments
        "assessments": getFakeAssessments(),
        "scheduledAssessments":scheduledAssessments,
        "assessmentLogs": loggedAssessments,

        # Activities
        "activities": getFakeActivities(),

        # Mood logs
        "moodLogs": loggedMood
    }


def getRandomInteger(minInclusive, maxExclusive):
    return int(np.random.randint(low=minInclusive, high=maxExclusive))


def getRandomItem(enum):
    return np.random.choice(enum, 1)[0]


def getRandomBoolean():
    return np.random.randint(0, 2) == 0


def sample(enum, count):
    return np.random.choice(enum, count, replace=False)


def getRandomFlags(enum):
    flags = dict()
    for key in enum:
        flags[key.value] = getRandomBoolean()

    return flags


def getRandomStates(enum, options):
    flags = dict()
    for key in enum:
        flags[key.value] = getRandomItem(options).value

    return flags


def getFakeAssessments():
    return [
        {
            "assessmentId": "mood" if a.value == "Mood Logging" else "medication" if a.value == "Medication Tracking" else a.value.lower(),
            "assessmentName": a.value,
            "frequency": getRandomItem(AssessmentFrequency).value,
            "dayOfWeek": getRandomItem(DayOfWeek).value,
        }
        for a in AssessmentType
    ]


def getFakeAssessmentDataPoint(assessmentType):
    points = dict()
    if assessmentType == "PHQ-9":
        for q in phq9Assessment.get("questions", []):
            points[q["id"]] = getRandomInteger(0, 4)
        return points
    elif assessmentType == "GAD-7":
        for q in gad7Assessment.get("questions", []):
            points[q["id"]] = getRandomInteger(0, 4)
        return points
    elif assessmentType == "Mood Logging":
        return {"Mood": getRandomInteger(1, 11)}
    elif assessmentType == "Medication Tracking":
        return {"Adherence": getRandomInteger(1, 6)}
    else:
        return {}


def getFakeScheduledAssessment(assessment):

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
    dowValues = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    for idx in range(len(dowValues)):
        if assessment["dayOfWeek"] == dowValues[idx]:
            dow = idx
            break

    dueDate = datetime.today() + timedelta(days=7 - date.today().weekday() + dow)

    # 10 assessments in the past and 10 in the future
    scheduled = []
    for idx in range(-10, 10):
        scheduled.append({
            "scheduleId": "Scheduled %d" % idx,
            "assessmentId": assessment["assessmentId"],
            "assessmentName": assessment["assessmentName"],
            "dueDate": dueDate + timedelta(days=freq * idx)
        })

    return scheduled


def getFakeAssessmentDataPoints(assessmentType):
    if assessmentType == "Mood Logging":
        return [
        {
            "assessmentDataId": "%s-%d" % (assessmentType, idx),
            "assessmentType": assessmentType,
            "date": datetime.now()
            - timedelta(hours=getRandomInteger(4, 48) + idx * getRandomInteger(0, 120)),
            "pointValues": getFakeAssessmentDataPoint(assessmentType),
            "comment": shortLorem.paragraph(),
            "patientSubmitted": getRandomBoolean()
        }
        for idx in range(getRandomInteger(5, 10))
    ]
    else:
        data = [
            {
                "assessmentDataId": "%s-%d" % (assessmentType, idx),
                "assessmentType": assessmentType,
                "date": datetime.now() + timedelta(days=14)
                - timedelta(days=getRandomInteger(0, 3) + idx * getRandomInteger(5, 8)),
                "pointValues": getFakeAssessmentDataPoint(assessmentType),
                "comment": shortLorem.paragraph(),
                "patientSubmitted": getRandomBoolean()
            }
            for idx in range(getRandomInteger(5, 10))
        ]

        for d in data:
            if d["date"] > datetime.now():
                d["pointValues"] = None
                d["comment"] = None
                d["patientSubmitted"] = None

        return data


def getFakeSessions():
    sessionCount = getRandomInteger(1, 10)

    randomReferrals = getRandomStates(Referral, ReferralStatus)
    referrals = []
    for referral in randomReferrals:
        if randomReferrals[referral] != "Not Referred":
            referrals.append({
                "referralType": referral,
                "referralStatus": randomReferrals[referral]
            })

    return [
        {
            "sessionId": "Initial assessment" if idx == 0 else "session-%d" % idx,
            "date": datetime.now()
            - timedelta(
                days=getRandomInteger(-2, 2)
                + (sessionCount - idx) * getRandomInteger(13, 18)
            ),
            "sessionType": getRandomItem(SessionType).value,
            "billableMinutes": int(getRandomItem([30, 45, 60, 80])),
            "medicationChange": shortLorem.sentence() if getRandomBoolean() else "",
            "currentMedications": shortLorem.sentence() if getRandomBoolean() else "",
            "behavioralStrategyChecklist": getRandomFlags(BehavioralStrategyChecklist),
            "behavioralStrategyOther": shortLorem.sentence()
            if getRandomBoolean()
            else "",
            "behavioralActivationChecklist": getRandomFlags(
                BehavioralActivationChecklist
            ),
            "referrals": referrals,
            "otherRecommendations": shortLorem.sentence(),
            "sessionNote": lorem.paragraph(),
        }
        for idx in range(sessionCount)
    ]


def getFakeActivities():
    return [
        {
            "activityId": "%s" % idx,
            "activityName": shortLorem.sentence(),
            "moodData": getFakeAssessmentDataPoints("Mood Logging"),
        }
        for idx in range(getRandomInteger(1, 3))
    ]
