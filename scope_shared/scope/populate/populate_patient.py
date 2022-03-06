import copy
import pymongo.database
from typing import List

import scope.database.patients


def create_patients(
    *,
    database: pymongo.database.Database,
    create_patients: List[dict],
) -> List[dict]:
    result: List[dict] = []
    for create_patient_current in create_patients:
        created_patient = _create_patient(
            database=database,
            name=create_patient_current["name"],
            mrn=create_patient_current["MRN"],
            create_patient=create_patient_current,
        )

        result.append(created_patient)

    return result


def _create_patient(
    *,
    database: pymongo.database.Database,
    name: str,
    mrn: str,
    create_patient: dict,
) -> dict:
    # Consistency check
    if not all([
        name == create_patient["name"],
        mrn == create_patient["MRN"],
    ]):
        raise ValueError()

    # Create the patient
    patient_identity_document = scope.database.patients.create_patient(
        database=database,
        patient_name=name,
        patient_mrn=mrn,
    )

    # Update the patient object
    created_patient = copy.deepcopy(create_patient)
    created_patient.update({
        "patientId": patient_identity_document[
            scope.database.patients.PATIENT_IDENTITY_SEMANTIC_SET_ID
        ],
    })

    return created_patient
