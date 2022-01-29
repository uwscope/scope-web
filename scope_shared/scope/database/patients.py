import base64
import hashlib
import pymongo.database
from typing import List
from typing import Optional
import uuid

import scope.database.collection_utils

PATIENT_DOCUMENT_TYPE = "patient"
PATIENTS_COLLECTION = "patients"


def _generate_patient_id() -> str:
    """
    Generate a patient_id that:
    - Is guaranteed to be URL safe.
    - Is guaranteed to be compatible with MongoDB collection naming.
    - Is expected to be unique.
    """

    # Obtain uniqueness
    generated_uuid = uuid.uuid4()
    # Manage length so these don't seem obscenely long
    generated_digest = hashlib.blake2b(generated_uuid.bytes, digest_size=8).digest()
    # Obtain URL safety and MongoDB collection name compatibility.
    generated_base64 = base64.b32encode(generated_digest).decode("ascii").casefold()

    # Remove terminating "=="
    clean_generated_base64 = generated_base64.rstrip("=")

    return clean_generated_base64


def _patient_collection_name(*, patient_id: str) -> str:
    return "patient_{}".format(patient_id)


def create_patient(
    *,
    database: pymongo.database.Database,
) -> dict:
    """
    Create a patient document and collection, return the patient document.
    """

    patients_collection = database.get_collection(PATIENTS_COLLECTION)

    # Obtain a unique ID and collection name for the patient.
    # A set element with the generated_patient_id ensures the patient_id is unique.
    # We can therefore also use it as our collection name.
    generated_patient_id = _generate_patient_id()
    generated_patient_collection = _patient_collection_name(
        patient_id=generated_patient_id
    )

    # Store the patient document
    patient_document = {
        "collection": generated_patient_collection,
    }
    result = scope.database.collection_utils.put_set_element(
        collection=patients_collection,
        document_type=PATIENT_DOCUMENT_TYPE,
        set_id=generated_patient_id,
        document=patient_document,
    )
    patient_document = result.document

    # Create the patient collection with a sentinel document
    patient_collection = database.get_collection(generated_patient_collection)
    result = scope.database.collection_utils.put_singleton(
        collection=patient_collection,
        document_type="sentinel",
        document={},
    )

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
    # There is likely a race condition here, but our semantics for destructive deletion are weak.
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
