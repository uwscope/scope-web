import base64
import hashlib
import uuid
from typing import List, Optional

import pymongo.database
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
    generated_digest = hashlib.blake2b(generated_uuid.bytes, digest_size=6).digest()
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
        set_id=generated_patient_id,
        document=patient_document,
    )
    patient_document = result.document

    return patient_document


# TODO: Remove once auth/login works.
# This method is similar to create_patient except it takes a static patient_id.
# Additionally, (1) it drops the patien_<patient_id> collection before re-creating it, and
# (2) deletes the patient set with `_set_id=patient_id` from patients collection.
def create_persistent_patient(
    *,
    database: pymongo.database.Database,
    patient_id: str,
) -> dict:
    """
    Create a patient document and collection using provided patient_id, return the patient document.
    """

    assert patient_id == "persistent"  # Remove if you expect any other patient_id.

    patients_collection = database.get_collection(PATIENTS_COLLECTION)

    # Obtain a collection name for the given patient ID.
    generated_patient_collection = _patient_collection_name(patient_id=patient_id)

    # Drop the persistent patient collection if it exists.
    database.drop_collection(generated_patient_collection)

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

    # Delete the persistent patient set element from patients collection to avoid duplicate key error.
    scope.database.collection_utils.delete_set_element(
        collection=patients_collection,
        document_type=PATIENT_DOCUMENT_TYPE,
        set_id=patient_id,
        destructive=True,
    )

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
