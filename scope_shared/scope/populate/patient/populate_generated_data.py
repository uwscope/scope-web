import copy
import pymongo.database

import scope.database.patients
import scope.schema
import scope.schema_utils as schema_utils

ACTION_NAME = "populate_generated_data"


def _ensure_valid(
    *,
    patient_config: dict,
) -> None:
    if "actions" not in patient_config:
        raise ValueError('patient_config["actions"] not found', patient_config)
    if ACTION_NAME not in patient_config["actions"]:
        raise ValueError(
            'ACTION_NAME not found in patient_config["actions"]', patient_config
        )


def populate_generated_data(
    *,
    database: pymongo.database.Database,
    patient_config: dict,
) -> dict:
    # Ensure a valid setup
    _ensure_valid(patient_config=patient_config)

    # Get the patient identity document
    patient_identity_document = scope.database.patients.get_patient_identity(
        database=database,
        patient_id=patient_config["patientId"],
    )

    # Mark the action complete
    updated_patient_config = copy.deepcopy(patient_config)
    updated_patient_config["actions"].remove(ACTION_NAME)

    return updated_patient_config
