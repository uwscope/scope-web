import copy
import pymongo.database

import scope.database.patients


def create_patient(
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
