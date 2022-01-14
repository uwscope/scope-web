import hashlib
import re
from typing import List, Optional

import bson
import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results

# NOTE: Keep this for `invoke database.dev.reset`
PATIENTS_COLLECTION_NAME = "patients"


def collection_for_patient(*, patient_name: str):
    """
    Obtain the name of the collection for a specified patient.

    Collection name will therefore be 'patient_' followed by hex encoding of an MD5 hash of the patient name.
    """
    # NOTE: Needs to be changed. There will be hash collisions for people with same names.
    return "patient_{}".format(hashlib.md5(patient_name.encode("utf-8")).digest().hex())


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
        # Find the document with highest `v`.
        found = collection.find_one(filter=query, sort=[("_rev", pymongo.DESCENDING)])
        if found is not None:
            # To serialize object and to avoid `TypeError: Object of type ObjectId is not JSON serializable` error, convert _id in document to string.
            if "_id" in found:
                found["_id"] = str(found["_id"])
        patient[query["_type"]] = found

    # Find unique session ids and then get document with latest _rev from them.
    pipeline = [
        {"$match": {"_type": "session"}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                "_id": "$_session_id",
                "latest_session_document": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$latest_session_document"}},
    ]

    found_sessions = list(collection.aggregate(pipeline))
    if found_sessions is not None:
        for found_session in found_sessions:
            if "_id" in found_session:
                found_session["_id"] = str(found_session["_id"])

    patient["sessions"] = found_sessions

    return patient


def create_patient(*, database: pymongo.database.Database, patient: dict) -> str:
    """
    Initialize a patient collection.

    Initialize the collection with multiple subschema documents and return the collection name.
    """

    identity = patient.get("identity")
    patient_profile = patient.get("patientProfile")
    clinical_history = patient.get("clinicalHistory")
    values_inventory = patient.get("valuesInventory")
    safety_plan = patient.get("safetyPlan")
    sessions = patient.get("sessions")

    patient_collection_name = collection_for_patient(patient_name=identity["name"])

    # Get or create a patients collection
    patients_collection = database.get_collection(patient_collection_name)

    # Create unique index.
    patients_collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
            ("_session_id", pymongo.DESCENDING),
            ("_assessment_id", pymongo.DESCENDING),
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
        patients_collection.insert_one(document=identity)
        patients_collection.insert_one(document=patient_profile)
        patients_collection.insert_one(document=clinical_history)
        patients_collection.insert_one(document=values_inventory)
        patients_collection.insert_one(document=safety_plan)
        patients_collection.insert_many(documents=sessions)

    return patient_collection_name


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
