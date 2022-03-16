import copy
import pymongo.database
from typing import List

import scope.database.patients
import scope.populate.patient.update_identity_cognito_account_from_config

def create_patients_from_configs(
    *,
    database: pymongo.database.Database,
    create_patient_configs: List[dict],
) -> List[dict]:
    result: List[dict] = []
    for create_patient_config_current in create_patient_configs:
        created_patient_config = _create_patient_from_config(
            database=database,
            name=create_patient_config_current["name"],
            mrn=create_patient_config_current["MRN"],
            create_patient_config=create_patient_config_current,
        )

        result.append(created_patient_config)

    return result


def _create_patient_from_config(
    *,
    database: pymongo.database.Database,
    name: str,
    mrn: str,
    create_patient_config: dict,
) -> dict:
    # Consistency check:
    # - All patient creates should include name and MRN per schema
    if not all(
        [
            name == create_patient_config["name"],
            mrn == create_patient_config["MRN"],
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
    created_patient_config = copy.deepcopy(create_patient_config)
    created_patient_config.update(
        {
            "patientId": patient_identity_document[
                scope.database.patients.PATIENT_IDENTITY_SEMANTIC_SET_ID
            ],
        }
    )

    # Specify follow-up actions
    actions = created_patient_config.get("actions", [])
    actions = actions + [
        # All new patients require default data
        "populate_default_data",
    ]
    if "account" in created_patient_config:
        # New patients with an account must have identity updated for that account
        actions = actions + [
            scope.populate.patient.update_identity_document_from_account_config.ACTION_NAME
        ]

    created_patient_config["actions"] = actions


    return created_patient_config
