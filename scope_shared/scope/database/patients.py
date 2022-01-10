import hashlib
import re
from typing import List, Optional

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

    return "patient_{}".format(hashlib.md5(patient_name.encode("utf-8")).digest().hex())


def create_patient(*, database: pymongo.database.Database, patient: dict) -> str:
    """
    Initialize a patient collection.

    Initialize the collection with multiple subchema documents and return the collection name.
    """

    identity = patient["identity"]
    patient_profile = patient["patientProfile"]
    clinical_history = patient["clinicalHistory"]
    values_inventory = patient["valuesInventory"]
    safety_plan = patient["safetyPlan"]

    patient_collection_name = collection_for_patient(patient_name=identity["name"])

    # Get or create a patients collection
    patients_collection = database.get_collection(patient_collection_name)

    # Ensure an identity document exists.
    result = patients_collection.find_one(
        filter={
            "type": "identity",
        }
    )
    if result is None:
        # NOTE: Talk to James about this.
        patients_collection.insert_one(document=identity)
        patients_collection.insert_one(document=patient_profile)
        patients_collection.insert_one(document=clinical_history)
        patients_collection.insert_one(document=values_inventory)
        patients_collection.insert_one(document=safety_plan)

    # Create unique index on (`type`, `v`)
    patients_collection.create_index(
        [("type", pymongo.ASCENDING), ("_rev", pymongo.DESCENDING)], unique=True
    )

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

    collection = database.get_collection(name=collection_name)

    patient = {"type": "patient"}

    queries = [
        {
            "type": "identity",
        },
        {
            "type": "patientProfile",
        },
        {
            "type": "clinicalHistory",
        },
        {
            "type": "valuesInventory",
        },
        {
            "type": "safetyPlan",
        },
    ]

    for query in queries:
        # Find the document with highest `v`.
        found = collection.find_one(filter=query, sort=[("_rev", pymongo.DESCENDING)])
        # To serialize object and to avoid `TypeError: Object of type ObjectId is not JSON serializable` error, convert _id in document to string.
        if "_id" in found:
            found["_id"] = str(found["_id"])
        patient[query["type"]] = found

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
        patient = {"type": "patient"}
        # NOTE: Validate latency.
        collection = database.get_collection(name=patient_collection)
        queries = [
            {
                "type": "identity",
            },
            {
                "type": "patientProfile",
            },
            {
                "type": "clinicalHistory",
            },
            {
                "type": "valuesInventory",
            },
            {
                "type": "safetyPlan",
            },
        ]

        for query in queries:
            # Find the document with highest `v`.
            found = collection.find_one(
                filter=query, sort=[("_rev", pymongo.DESCENDING)]
            )
            # To serialize object and to avoid `TypeError: Object of type ObjectId is not JSON serializable` error, convert _id in document to string.
            if "_id" in found:
                found["_id"] = str(found["_id"])
            patient[query["type"]] = found

        patients.append(patient)

    # TODO: Verify schema against each patient in patients

    return patients
