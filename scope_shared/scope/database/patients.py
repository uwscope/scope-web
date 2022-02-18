import base64
import hashlib
import pymongo.database
from typing import List
from typing import Optional
import uuid

import scope.database.collection_utils

PATIENT_DOCUMENT_TYPE = "patient"
PATIENTS_COLLECTION = "patients"


def _patient_collection_name(*, patient_id: str) -> str:
    return "patient_{}".format(patient_id)


def create_patient(
    *, database: pymongo.database.Database, patient_id: str = None
) -> dict:
    """
    Create a patient document and collection, return the patient document.
    """

    patients_collection = database.get_collection(PATIENTS_COLLECTION)

    # Obtain a unique ID and collection name for the patient.
    # A set element with the generated_patient_id ensures the patient_id is unique.
    # We can therefore also use it as our collection name.
    if patient_id is None:
        patient_id = scope.database.collection_utils.generate_unique_id()

    generated_patient_collection = _patient_collection_name(patient_id=patient_id)

    # Create the patient collection with a sentinel document
    patient_collection = database.get_collection(generated_patient_collection)
    result = scope.database.collection_utils.put_singleton(
        collection=patient_collection,
        document_type="sentinel",
        document={},
    )

    # Create the index on the patient collection
    scope.database.collection_utils.ensure_index(collection=patient_collection)

    # Atomically store the patient document.
    # Do this last, because it means all other steps have already succeeded.
    patient_document = {
        "collection": generated_patient_collection,
    }
    result = scope.database.collection_utils.put_set_element(
        collection=patients_collection,
        document_type=PATIENT_DOCUMENT_TYPE,
        set_id=patient_id,
        document=patient_document,
    )
    patient_document = result.document

    return patient_document


def delete_patient(
    *,
    database: pymongo.database.Database,
    patient_id: str,
    destructive: bool,
):
    """
    Delete a patient document and collection.
    """

    if not destructive:
        raise NotImplementedError()

    patients_collection = database.get_collection(PATIENTS_COLLECTION)

    # Confirm the patient exists.
    existing_document = scope.database.collection_utils.get_set_element(
        collection=patients_collection,
        document_type=PATIENT_DOCUMENT_TYPE,
        set_id=patient_id,
    )
    if existing_document is None:
        return False

    # Delete the document and the database.
    database.drop_collection(existing_document["collection"])
    scope.database.collection_utils.delete_set_element(
        collection=patients_collection,
        document_type=PATIENT_DOCUMENT_TYPE,
        set_id=patient_id,
        destructive=destructive,
    )

    return True


def get_patient(
    *,
    database: pymongo.database.Database,
    patient_id: str,
) -> Optional[dict]:
    """
    Retrieve a patient document from PATIENTS_COLLECTION.
    """

    patients_collection = database.get_collection(PATIENTS_COLLECTION)

    return scope.database.collection_utils.get_set_element(
        collection=patients_collection,
        document_type=PATIENT_DOCUMENT_TYPE,
        set_id=patient_id,
    )


def get_patients(
    *,
    database: pymongo.database.Database,
) -> Optional[List[dict]]:
    """
    Retrieve all patient documents from PATIENTS_COLLECTION.
    """

    patients_collection = database.get_collection(PATIENTS_COLLECTION)

    return scope.database.collection_utils.get_set(
        collection=patients_collection,
        document_type=PATIENT_DOCUMENT_TYPE,
    )
