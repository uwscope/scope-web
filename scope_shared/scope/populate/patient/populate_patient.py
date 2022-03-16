import copy
import pymongo.database
from typing import List

import scope.database.patients
import scope.schema
import scope.schema_utils


def create_patients_from_configs(
    *,
    database: pymongo.database.Database,
    create_patient_configs: List[dict],
) -> List[dict]:
    result: List[dict] = []
    for create_patient_current in create_patient_configs:
        created_patient = _create_patient_from_config(
            database=database,
            name=create_patient_current["name"],
            mrn=create_patient_current["MRN"],
            create_patient=create_patient_current,
        )

        result.append(created_patient)

    return result


def _create_patient_from_config(
    *,
    database: pymongo.database.Database,
    name: str,
    mrn: str,
    create_patient: dict,
) -> dict:
    # Consistency check:
    # - All patient creates should include name and MRN per schema
    if not all(
        [
            name == create_patient["name"],
            mrn == create_patient["MRN"],
        ]
    ):
        raise ValueError()

    # Create the patient
    patient_identity_document = scope.database.patients.create_patient(
        database=database,
        patient_name=name,
        patient_mrn=mrn,
    )

    # Update the patient object
    created_patient = copy.deepcopy(create_patient)
    created_patient.update(
        {
            "patientId": patient_identity_document[
                scope.database.patients.PATIENT_IDENTITY_SEMANTIC_SET_ID
            ],
        }
    )

    return created_patient


def ensure_patient_identities(
    *,
    database: pymongo.database.Database,
    patients: List[dict],
) -> None:
    for patient_current in patients:
        # Consistency check:
        # - Should only be called with existing patients
        # - All patients should include patientId per schema
        if not all(
            [
                "patientId" in patient_current,
            ]
        ):
            raise ValueError()

        # Only ensure identities for patients that have an account
        if "account" in patient_current:
            _ensure_patient_identity(database=database, patient=patient_current)


def _ensure_patient_identity(
    *,
    database: pymongo.database.Database,
    patient: dict,
) -> None:
    # Consistency check:
    # - Should only be called for patients with an account
    # - Should only be called after account creation
    # - Account should include cognitoId and email per schema
    if not all(
        [
            "account" in patient,
            "create" not in patient["account"],
            "existing" in patient["account"],
            "cognitoId" in patient["account"]["existing"],
            "email" in patient["account"]["existing"],
        ]
    ):
        raise ValueError()

    patient_identity_document = scope.database.patients.get_patient_identity(
        database=database,
        patient_id=patient["patientId"],
    )

    # Check for a need to update the identity document
    update_identity_document = False
    if not update_identity_document:
        update_identity_document = "cognitoAccount" not in patient_identity_document
    if not update_identity_document:
        update_identity_document = (
            patient_identity_document["cognitoAccount"]["cognitoId"]
            != patient["account"]["existing"]["cognitoId"]
        )
    if not update_identity_document:
        update_identity_document = (
            patient_identity_document["cognitoAccount"]["email"]
            != patient["account"]["existing"]["email"]
        )

    # Perform the update if needed
    if update_identity_document:
        patient_identity_document = copy.deepcopy(patient_identity_document)

        del patient_identity_document["_id"]
        patient_identity_document.update(
            {
                "cognitoAccount": {
                    "cognitoId": patient["account"]["existing"]["cognitoId"],
                    "email": patient["account"]["existing"]["email"],
                }
            }
        )

        scope.schema_utils.raise_for_invalid_schema(
            data=patient_identity_document,
            schema=scope.schema.patient_identity_schema,
        )

        result = scope.database.patients.put_patient_identity(
            database=database,
            patient_id=patient["patientId"],
            patient_identity=patient_identity_document,
        )
        if not result.inserted_count == 1:
            raise RuntimeError()
