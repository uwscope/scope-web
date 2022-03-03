import pymongo.database
from typing import List

import scope.database.patients
import scope.database.providers


def populate_from_config(
    *,
    database: pymongo.database.Database,
    populate_config: dict
) -> dict:
    """
    Populate from a provided config.

    Return a new state of the populate config.
    """

    created_patients = _create_patients(
        database=database,
        create_patients=populate_config["patients"]["create"],
    )
    populate_config["patients"]["create"] = []
    populate_config["patients"]["existing"].extend(created_patients)

    created_providers = _create_providers(
        database=database,
        create_providers=populate_config["providers"]["create"],
    )
    populate_config["providers"]["create"] = []
    populate_config["providers"]["existing"].extend(created_providers)

    return populate_config


def _create_patients(
    *,
    database: pymongo.database.Database,
    create_patients: List[dict],
) -> List[dict]:
    result: List[dict] = []
    for create_patient_current in create_patients:
        patient_identity_document = scope.database.patients.create_patient(
            database=database,
            patient_name=create_patient_current["name"],
            patient_mrn=create_patient_current["MRN"],
        )

        created_provider = {
            "patientId": patient_identity_document[scope.database.patients.PATIENT_IDENTITY_SEMANTIC_SET_ID],
            "name": patient_identity_document["name"],
            "MRN": patient_identity_document["MRN"],
        }

        result.append(created_provider)

    return result


def _create_providers(
    *,
    database: pymongo.database.Database,
    create_providers: List[dict],
) -> List[dict]:
    result: List[dict] = []
    for create_provider_current in create_providers:
        provider_identity_document = scope.database.providers.create_provider(
            database=database,
            name=create_provider_current["name"],
            role=create_provider_current["role"],
        )

        created_provider = {
            "providerId": provider_identity_document[scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID],
            "name": provider_identity_document["name"],
            "role": provider_identity_document["role"],
        }

        result.append(created_provider)

    return result
