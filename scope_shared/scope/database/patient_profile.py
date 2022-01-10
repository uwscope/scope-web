from typing import List, Optional

import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results


def get_patient_profile(
    *, database: pymongo.database.Database, collection_name: str
) -> Optional[dict]:
    """
    Retrieve "patientProfile" document.
    """
    collection = database.get_collection(name=collection_name)

    query = {
        "type": "patientProfile",
    }

    # Find the document with highest `v`.
    patient_profile = collection.find_one(
        filter=query, sort=[("_rev", pymongo.DESCENDING)]
    )

    if "_id" in patient_profile:
        patient_profile["_id"] = str(patient_profile["_id"])
    # TODO: Verify schema against patient-profile json.

    return patient_profile


def create_patient_profile(
    *, database: pymongo.database.Database, collection_name: str, patient_profile: dict
) -> pymongo.results.InsertOneResult:
    """
    Create the "patientProfile" document.
    """

    collection = database.get_collection(name=collection_name)

    try:
        result = collection.insert_one(document=patient_profile)
        return result
    except pymongo.errors.DuplicateKeyError:
        return None
