import datetime
import pymongo.database
import pytz
from typing import List, Optional

import scope.database.date_utils as date_utils
import scope.database.collection_utils as collection_utils
import scope.database.patient.assessments
import scope.database.patient.clinical_history
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.values_inventory
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils

PATIENT_IDENTITY_COLLECTION = "patients"

PATIENT_IDENTITY_DOCUMENT_TYPE = "patientIdentity"
PATIENT_IDENTITY_SEMANTIC_SET_ID = "patientId"


def _patient_collection_name(*, patient_id: str) -> str:
    return "patient_{}".format(patient_id)


def create_patient(
    *,
    database: pymongo.database.Database,
    patient_name: str,
    patient_mrn: str,
) -> dict:
    """
    Create a patient. This includes:
    - Generate a new patient_id, ensure it is unique.
    - Call ensure_patient_collection.
    - Call ensure_patient_documents.
    - Call ensure_patient_identity.
    """

    # Create a unique ID for the patient, use that to create a collection name.
    patient_id = scope.database.collection_utils.generate_set_id()
    generated_patient_collection_name = _patient_collection_name(patient_id=patient_id)

    # Ensure this patient id and collection do not already exist.
    if get_patient_identity(database=database, patient_id=patient_id) is not None:
        raise ValueError('Patient identity "{}" already exists'.format(patient_id))
    if generated_patient_collection_name in database.list_collection_names():
        raise ValueError(
            'Patient collection "{}" already exists'.format(
                generated_patient_collection_name
            )
        )

    # Create the patient collection
    patient_collection = ensure_patient_collection(
        database=database,
        patient_id=patient_id,
    )

    # Ensure necessary documents
    ensure_patient_documents(
        database=database,
        patient_collection=patient_collection,
        patient_id=patient_id,
        patient_name=patient_name,
        patient_mrn=patient_mrn,
    )

    # Create the patient identity document.
    # Do this last, because it means all other steps have already succeeded.
    patient_identity_document = ensure_patient_identity(
        database=database,
        patient_collection=patient_collection,
        patient_id=patient_id,
        patient_name=patient_name,
        patient_mrn=patient_mrn,
    )

    return patient_identity_document


def delete_patient(
    *,
    database: pymongo.database.Database,
    patient_id: str,
    destructive: bool,
):
    """
    Delete a patient identity and collection.
    Delete any of an identity of a collection, in case database is in an incomplete state.
    """

    if not destructive:
        raise NotImplementedError()

    exists: bool = False

    # If the patient identity exists, delete it.
    patient_identity_document = get_patient_identity(
        database=database,
        patient_id=patient_id,
    )

    if patient_identity_document:
        exists = True
        scope.database.collection_utils.delete_set_element(
            collection=database.get_collection(PATIENT_IDENTITY_COLLECTION),
            document_type=PATIENT_IDENTITY_DOCUMENT_TYPE,
            set_id=patient_id,
            destructive=destructive,
        )

    # If the patient collection exists, delete it.
    if patient_identity_document:
        patient_collection_name: str = patient_identity_document["collection"]
    else:
        patient_collection_name: str = _patient_collection_name(patient_id=patient_id)

    if patient_collection_name in database.list_collection_names():
        exists = True
        database.drop_collection(name_or_collection=patient_collection_name)

    return exists


def ensure_patient_collection(
    *,
    database: pymongo.database.Database,
    patient_id: str,
) -> pymongo.collection.Collection:
    """
    Ensure a patient collection exists and can be used for storing patient documents.
    This function should be idempotent, it may be called many times on a collection that already exists.
    """

    patient_collection_name = _patient_collection_name(patient_id=patient_id)
    patient_collection = database.get_collection(patient_collection_name)

    # If the sentinel document does not already exist, create it.
    sentinel_document = scope.database.collection_utils.get_singleton(
        collection=patient_collection,
        document_type="sentinel",
    )
    if sentinel_document is None:
        result = scope.database.collection_utils.put_singleton(
            collection=patient_collection,
            document_type="sentinel",
            document={},
        )

    # Ensure the collection has the desired index
    scope.database.collection_utils.ensure_index(collection=patient_collection)

    return patient_collection


def ensure_patient_documents(
    *,
    database: pymongo.database.Database,
    patient_collection: pymongo.collection.Collection,
    patient_id: str,
    patient_name: str,
    patient_mrn: str,
):
    """
    Ensure a patient has a minimal set of documents.
    This function should be idempotent, it may be called many times on a collection that already exists.
    These documents are intentionally minimal, intended mostly to ensure database state is well-defined.
    Any more complex or meaningful document creation should instead be configured in a populate script.
    """

    # Many documents have a required assignment datetime.
    # Generate a single value to consistently use as necessary
    datetime_assigned = scope.database.date_utils.format_datetime(
        pytz.utc.localize(datetime.datetime.utcnow())
    )

    # Minimal patient profile
    patient_profile_document = (
        scope.database.patient.patient_profile.get_patient_profile(
            collection=patient_collection,
        )
    )
    if patient_profile_document is None:
        patient_profile_document = {
            "_type": scope.database.patient.patient_profile.DOCUMENT_TYPE,
            "name": patient_name,
            "MRN": patient_mrn,
        }
        result = scope.database.patient.patient_profile.put_patient_profile(
            database=database,
            collection=patient_collection,
            patient_id=patient_id,
            patient_profile=patient_profile_document,
        )

    # Minimal clinical history
    clinical_history_document = (
        scope.database.patient.clinical_history.get_clinical_history(
            collection=patient_collection,
        )
    )
    if clinical_history_document is None:
        clinical_history_document = {
            "_type": scope.database.patient.clinical_history.DOCUMENT_TYPE,
        }
        result = scope.database.patient.clinical_history.put_clinical_history(
            collection=patient_collection,
            clinical_history=clinical_history_document,
        )

    # Minimal safety plan
    safety_plan_document = scope.database.patient.safety_plan.get_safety_plan(
        collection=patient_collection,
    )
    if safety_plan_document is None:
        safety_plan_document = {
            "_type": scope.database.patient.safety_plan.DOCUMENT_TYPE,
            "assigned": False,
            "assignedDateTime": datetime_assigned,
        }
        result = scope.database.patient.safety_plan.put_safety_plan(
            collection=patient_collection,
            safety_plan=safety_plan_document,
        )

    # Minimal values inventory
    values_inventory_document = (
        scope.database.patient.values_inventory.get_values_inventory(
            collection=patient_collection,
        )
    )
    if values_inventory_document is None:
        values_inventory_document = {
            "_type": scope.database.patient.values_inventory.DOCUMENT_TYPE,
            "assigned": False,
            "assignedDateTime": datetime_assigned,
        }
        result = scope.database.patient.values_inventory.put_values_inventory(
            collection=patient_collection,
            values_inventory=values_inventory_document,
        )

    # Minimal assessments
    for assessment_current in [
        scope.enums.AssessmentType.GAD7.value,
        scope.enums.AssessmentType.Medication.value,
        scope.enums.AssessmentType.PHQ9.value,
    ]:
        assessment_document = scope.database.patient.assessments.get_assessment(
            collection=patient_collection,
            set_id=assessment_current,
        )
        if assessment_document is None:
            assessment_document = {
                "_type": scope.database.patient.assessments.DOCUMENT_TYPE,
                "_set_id": assessment_current,
                scope.database.patient.assessments.SEMANTIC_SET_ID: assessment_current,
                "assigned": False,
                "assignedDateTime": datetime_assigned,
            }
            result = scope.database.patient.assessments.put_assessment(
                collection=patient_collection,
                set_id=assessment_current,
                assessment=assessment_document,
            )


def ensure_patient_identity(
    *,
    database: pymongo.database.Database,
    patient_collection: pymongo.collection.Collection,
    patient_id: str,
    patient_name: str,
    patient_mrn: str,
) -> dict:
    """
    Ensure a patient identity exists and can be used for storing patient documents.
    This function should be idempotent, it may be called many times on a collection that already exists.
    """

    patient_identity_document = get_patient_identity(
        database=database,
        patient_id=patient_id,
    )
    if patient_identity_document is None:
        patient_identity_document = {
            "_type": PATIENT_IDENTITY_DOCUMENT_TYPE,
            "name": patient_name,
            "MRN": patient_mrn,
            "collection": patient_collection.name,
        }
        result = put_patient_identity(
            database=database,
            patient_id=patient_id,
            patient_identity=patient_identity_document,
        )

        patient_identity_document = result.document

    # Return the created patient identity
    return patient_identity_document


def get_patient_identity(
    *,
    database: pymongo.database.Database,
    patient_id: str,
) -> Optional[dict]:
    """
    Retrieve a patient identity document.
    """

    patient_identity_collection = database.get_collection(PATIENT_IDENTITY_COLLECTION)

    return scope.database.collection_utils.get_set_element(
        collection=patient_identity_collection,
        document_type=PATIENT_IDENTITY_DOCUMENT_TYPE,
        set_id=patient_id,
    )


def put_patient_identity(
    *,
    database: pymongo.database.Database,
    patient_id: str,
    patient_identity: dict,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put a patient identity document.
    """

    # Enforce the schema
    schema_utils.raise_for_invalid_schema(
        schema=scope.schema.patient_identity_schema,
        data=patient_identity,
    )

    # Put the document
    patient_identity_collection = database.get_collection(PATIENT_IDENTITY_COLLECTION)

    return scope.database.collection_utils.put_set_element(
        collection=patient_identity_collection,
        document_type=PATIENT_IDENTITY_DOCUMENT_TYPE,
        semantic_set_id=PATIENT_IDENTITY_SEMANTIC_SET_ID,
        set_id=patient_id,
        document=patient_identity,
    )


def get_patient_identities(
    *,
    database: pymongo.database.Database,
) -> Optional[List[dict]]:
    """
    Retrieve all patient identity documents.
    """

    patient_identity_collection = database.get_collection(PATIENT_IDENTITY_COLLECTION)

    return scope.database.collection_utils.get_set(
        collection=patient_identity_collection,
        document_type=PATIENT_IDENTITY_DOCUMENT_TYPE,
    )
