import hashlib
import pstats
import re
from typing import List, Optional

import bson
import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results

# NOTE: Keep this for `invoke database.dev.reset`
PATIENTS_COLLECTION_NAME = "patients"


# TODO: relying on uniqueness of patient name seems highly problematic
def collection_for_patient(*, patient_name: str):
    """
    Obtain the name of the collection for a specified patient.

    NOTE: Check with James.
    """
    # return "patient_{}".format(str(bson.objectid.ObjectId()))
    return "patient_{}".format(hashlib.md5(patient_name.encode("utf-8")).digest().hex())


def _build_patient_array_documents(
    collection: pymongo.database.Collection, type: str, document_id_key
):
    """
    Helper function to stitch together array documents of "_type" such as "session", "caseReview".
    """
    # Filter on type. Then, group documents by document_id_key and get document with latest _rev.
    pipeline = [
        {"$match": {"_type": type}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                "_id": "${}".format(document_id_key),
                "latest_rev_document": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$latest_rev_document"}},
    ]

    found_documents = list(collection.aggregate(pipeline))
    if found_documents is not None:
        for fd in found_documents:
            if "_id" in fd:
                fd["_id"] = str(fd["_id"])

    return found_documents


def _build_patient_assessment_log_documents(
    collection: pymongo.database.Collection, type: str, document_id_key
):
    """
    Helper function to stitch together array documents of "_type" equal to "assessmentLog".
    """
    # Filter on type. Then, group documents by document_id_key and get document with latest _rev.
    pipeline = [
        {"$match": {"_type": type}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                # _id:{username:$username, age:$ge}
                "_id": {
                    "{}".format(document_id_key): "${}".format(document_id_key),
                    "assessmentName": "$assessmentName",
                },
                "latest_rev_document": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$latest_rev_document"}},
    ]

    found_documents = list(collection.aggregate(pipeline))
    if found_documents is not None:
        for fd in found_documents:
            if "_id" in fd:
                fd["_id"] = str(fd["_id"])

    return found_documents


def _build_patient_json(
    database: pymongo.database.Database, collection_name: str
) -> dict:
    collection = database.get_collection(name=collection_name)
    patient = {"_type": "patient"}
    queries = [
        {
            "_type": "identity",
        },
        {
            "_type": "patientProfile",
        },
        {
            "_type": "clinicalHistory",
        },
        {
            "_type": "valuesInventory",
        },
        {
            "_type": "safetyPlan",
        },
    ]

    for query in queries:
        # Find the document with highest `_rev`.
        found = collection.find_one(filter=query, sort=[("_rev", pymongo.DESCENDING)])
        if found is not None:
            # To serialize object and to avoid `TypeError: Object of type ObjectId is not JSON serializable` error, convert _id in document to string.
            if "_id" in found:
                found["_id"] = str(found["_id"])
        patient[query["_type"]] = found

    patient["sessions"] = _build_patient_array_documents(
        collection=collection, type="session", document_id_key="_session_id"
    )
    
    patient["caseReviews"] = _build_patient_array_documents(
        collection=collection, type="caseReview", document_id_key="_review_id"
    )

    patient["assessments"] = _build_patient_array_documents(
        collection=collection, type="assessment", document_id_key="_assessment_id"
    )
    patient["scheduledAssessments"] = _build_patient_array_documents(
        collection=collection,
        type="scheduledAssessment",
        document_id_key="_schedule_id",
    )
    patient["assessmentLogs"] = _build_patient_array_documents(
        collection=collection, type="assessmentLog", document_id_key="_log_id"
    )

    patient["activities"] = _build_patient_array_documents(
        collection=collection, type="activity", document_id_key="_activity_id"
    )
    patient["scheduledActivities"] = _build_patient_array_documents(
        collection=collection,
        type="scheduledActivity",
        document_id_key="_schedule_id",
    )
    patient["activityLogs"] = _build_patient_array_documents(
        collection=collection, type="activityLog", document_id_key="_log_id"
    )

    patient["moodLogs"] = _build_patient_array_documents(
        collection=collection, type="moodLog", document_id_key="_log_id"
    )

    return patient


def create_patient(*, database: pymongo.database.Database, patient: dict) -> str:
    """
    Initialize a patient collection.

    Initialize the collection with multiple subschema documents and return the collection name.
    """

    identity = patient.get("identity")

    # Patient info
    patient_profile = patient.get("patientProfile")
    clinical_history = patient.get("clinicalHistory")
    # Values inventory and safety plan
    values_inventory = patient.get("valuesInventory")
    safety_plan = patient.get("safetyPlan")
    # Sessions
    sessions = patient.get("sessions")
    case_reviews = patient.get("caseReviews")
    # Assessments
    assessments = patient.get("assessments")
    scheduled_assessments = patient.get("scheduledAssessments")
    assessment_logs = patient.get("assessmentLogs")
    # Activities
    activities = patient.get("activities")
    scheduled_activities = patient.get("scheduledActivities")
    activity_logs = patient.get("activityLogs")
    # Mood logs
    mood_logs = patient.get("moodLogs")

    patient_collection_name = collection_for_patient(patient_name=identity["name"])

    # Get or create a patients collection
    patients_collection = database.get_collection(patient_collection_name)

    # Create unique index.
    patients_collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
            ("_session_id", pymongo.ASCENDING),  # session
            ("_review_id", pymongo.ASCENDING),  # caseReview
            ("_assessment_id", pymongo.ASCENDING),  # assessment
            (
                "_schedule_id",
                pymongo.ASCENDING,
            ),  # scheduledAssessment and scheduledActivity
            ("_log_id", pymongo.ASCENDING),  # assessmentLog and activityLog
            ("_activity_id", pymongo.ASCENDING),  # activity,
        ],
        unique=True,
        name="global_patient_index",
    )

    # Ensure no identity document exists.
    result = patients_collection.find_one(
        filter={
            "_type": "identity",
        }
    )
    if result is None:
        # TODO: Talk to James about this. Only insert documents if values exist in 'patient' dict
        if identity is not None:
            identity_result = patients_collection.insert_one(document=identity)
            patient["identity"].update({"_id": str(identity_result.inserted_id)})
        # Patient info
        if patient_profile is not None:
            patient_profile_result = patients_collection.insert_one(
                document=patient_profile
            )
            patient["patientProfile"].update(
                {"_id": str(patient_profile_result.inserted_id)}
            )
        if clinical_history is not None:
            clinical_history_restult = patients_collection.insert_one(
                document=clinical_history
            )
            patient["clinicalHistory"].update(
                {"_id": str(clinical_history_restult.inserted_id)}
            )
        # Values inventory and safety plan
        if values_inventory is not None:
            values_inventory_result = patients_collection.insert_one(
                document=values_inventory
            )
            patient["valuesInventory"].update(
                {"_id": str(values_inventory_result.inserted_id)}
            )
        if safety_plan is not None:
            safety_plan_result = patients_collection.insert_one(document=safety_plan)
            patient["safetyPlan"].update({"_id": str(safety_plan_result.inserted_id)})
        # Sessions
        if sessions is not None:
            sessions_result = patients_collection.insert_many(documents=sessions)
            for idx, s in enumerate(patient["sessions"]):
                s.update({"_id": str(sessions_result.inserted_ids[idx])})
        if case_reviews is not None:
            case_reviews_result = patients_collection.insert_many(
                documents=case_reviews
            )
            for idx, cr in enumerate(patient["caseReviews"]):
                cr.update({"_id": str(case_reviews_result.inserted_ids[idx])})
        # Assessments
        if assessments is not None:
            assessments_result = patients_collection.insert_many(documents=assessments)
            for idx, a in enumerate(patient["assessments"]):
                a.update({"_id": str(assessments_result.inserted_ids[idx])})
        if scheduled_assessments is not None:
            scheduled_assessments_result = patients_collection.insert_many(
                documents=scheduled_assessments
            )
            for idx, sa in enumerate(patient["scheduledAssessments"]):
                sa.update({"_id": str(scheduled_assessments_result.inserted_ids[idx])})
        if assessment_logs is not None:
            assessment_logs_result = patients_collection.insert_many(
                documents=assessment_logs
            )
            for idx, al in enumerate(patient["assessmentLogs"]):
                al.update({"_id": str(assessment_logs_result.inserted_ids[idx])})
        # Activities
        if activities is not None:
            activities_result = patients_collection.insert_many(documents=activities)
            for idx, a in enumerate(patient["activities"]):
                a.update({"_id": str(activities_result.inserted_ids[idx])})
        if scheduled_activities is not None:
            scheduled_activities_result = patients_collection.insert_many(
                documents=scheduled_activities
            )
            for idx, sa in enumerate(patient["scheduledActivities"]):
                sa.update({"_id": str(scheduled_activities_result.inserted_ids[idx])})
        if activity_logs is not None:
            activity_logs_result = patients_collection.insert_many(
                documents=activity_logs
            )
            for idx, al in enumerate(patient["activityLogs"]):
                al.update({"_id": str(activity_logs_result.inserted_ids[idx])})
        # Mood logs
        if mood_logs is not None:
            mood_logs_result = patients_collection.insert_many(documents=mood_logs)
            for idx, ml in enumerate(patient["moodLogs"]):
                ml.update({"_id": str(mood_logs_result.inserted_ids[idx])})

        return patient
    return None


def delete_patient(
    *, database: pymongo.database.Database, patient_collection_name: str
) -> pymongo.results.DeleteResult:
    """
    Delete "patient" collection with provided patient_collection_name.
    """

    database.drop_collection(name_or_collection=patient_collection_name)


def get_patient(
    *, database: pymongo.database.Database, collection_name: str
) -> Optional[dict]:
    """
    Retrieve "patient" document with provided patient collection.
    """

    # NOTE: If patient collection name doesn't exist, return None.
    # Maybe there is a better way to return a 404.
    if collection_name not in database.list_collection_names():
        return None

    patient = _build_patient_json(database, collection_name)

    return patient


def get_patients(*, database: pymongo.database.Database) -> List[dict]:
    """
    Retrieve all "patient" documents.
    """
    collections = database.list_collection_names()

    # Patient collection names start with `patient_`
    regex_match_string = "patient_(.*)"
    patient_collections = [
        collection
        for collection in collections
        if re.match(regex_match_string, collection)
    ]

    patients = []

    for patient_collection in patient_collections:

        patient = _build_patient_json(database, patient_collection)

        patients.append(patient)

    # TODO: Verify schema against each patient in patients

    return patients
