from typing import List, Optional

import pymongo.database
import pymongo.results

PATIENTS_COLLECTION_NAME = "patients"


def create_patient(
    *, database: pymongo.database.Database, patient: dict
) -> pymongo.results.InsertOneResult:
    """
    Create the provided patient.
    """

    # TODO: Verify schema against patient

    collection = database.get_collection(name=PATIENTS_COLLECTION_NAME)

    result = collection.insert_one(document=patient)

    return result


def delete_patient(
    *, database: pymongo.database.Database, id: str
) -> pymongo.results.DeleteResult:
    """
    Delete "patient" document with provided id.
    """

    # TODO: Verify schema against patient

    collection = database.get_collection(name=PATIENTS_COLLECTION_NAME)

    query = {
        "type": "patient",
        "_id": id,
    }

    result = collection.delete_one(filter=query)

    return result


def get_patient(*, database: pymongo.database.Database, id: str) -> Optional[dict]:
    """
    Retrieve "patient" document with provided id.
    """
    collection = database.get_collection(name=PATIENTS_COLLECTION_NAME)

    query = {
        "type": "patient",
        "_id": id,
    }

    patient = collection.find_one(filter=query)

    # TODO: Verify schema against patient

    return patient


def get_patients(*, database: pymongo.database.Database) -> List[dict]:
    """
    Retrieve all "patient" documents.
    """
    collection = database.get_collection(name=PATIENTS_COLLECTION_NAME)

    query = {
        "type": "patient",
    }

    cursor = collection.find(filter=query)
    patients = list(cursor)

    # To serialize object, convert _id in document to string.
    for doc in patients:
        doc.update((k, str(v)) for k, v in doc.items() if k == "_id")

    # TODO: Verify schema against each patient in patients

    return patients
