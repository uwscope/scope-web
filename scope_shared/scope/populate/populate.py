import pymongo.database
from typing import List, Optional

import scope.database.patients
import scope.database.providers
import scope.populate.populate_fake

def populate_from_config(
    *,
    database: pymongo.database.Database,
    populate_config: dict
) -> dict:
    """
    Populate from a provided config.

    Return a new state of the populate config.
    """

    #
    # Create any "persistent" patient
    #
    if populate_config["patients"].get("create_persistent", False):
        created_patient = _create_persistent(
            database=database
        )
        del populate_config["patients"]["create_persistent"]

        if created_patient:
            populate_config["patients"]["existing"].append(created_patient)

    #
    # Create any "persistentempty" patient
    #
    if populate_config["patients"].get("create_persistent_empty", False):
        created_patient = _create_persistent_empty(
            database=database
        )
        del populate_config["patients"]["create_persistent_empty"]

        if created_patient:
            populate_config["patients"]["existing"].append(created_patient)

    #
    # Create any fake patients
    #
    if "create_fake" in populate_config["patients"]:
        created_patients = _create_fake_patients(
            database=database,
            create_fake=populate_config["patients"]["create_fake"]
        )
        del populate_config["patients"]["create_fake"]

        populate_config["patients"]["existing"].extend(created_patients)

    #
    # Create any fake empty patients
    #
    if "create_fake_empty" in populate_config["patients"]:
        created_patients = _create_fake_empty_patients(
            database=database,
            create_fake_empty=populate_config["patients"]["create_fake_empty"]
        )
        del populate_config["patients"]["create_fake_empty"]

        populate_config["patients"]["existing"].extend(created_patients)

    #
    # Create specified patients
    #
    created_patients = _create_patients(
        database=database,
        create_patients=populate_config["patients"]["create"],
    )
    populate_config["patients"]["create"] = []
    populate_config["patients"]["existing"].extend(created_patients)

    #
    # Create specified providers
    #
    created_providers = _create_providers(
        database=database,
        create_providers=populate_config["providers"]["create"],
    )
    populate_config["providers"]["create"] = []
    populate_config["providers"]["existing"].extend(created_providers)

    return populate_config


def _create_fake_patients(
    *,
    database: pymongo.database.Database,
    create_fake: int,
) -> List[dict]:
    created_patients = []
    for _ in range(create_fake):
        created_patient = scope.populate.populate_fake.populate_fake_patient(
            database=database
        )
        created_patients.append(created_patient)

    return created_patients


def _create_fake_empty_patients(
        *,
        database: pymongo.database.Database,
        create_fake_empty: int,
) -> List[dict]:
    created_patients = []
    for _ in range(create_fake_empty):
        created_patient = scope.populate.populate_fake.populate_fake_patient_empty(
            database=database
        )
        created_patients.append(created_patient)

    return created_patients


def _create_persistent(
    *,
    database: pymongo.database.Database,
) -> Optional[dict]:
    # To be idempotent, do not attempt to create if patient already exists
    if scope.database.patients.get_patient_identity(
        database=database,
        patient_id="persistent"
    ):
        return

    created_patient = scope.populate.populate_fake.populate_fake_patient(
        database=database,
        patient_id="persistent"
    )

    return created_patient


def _create_persistent_empty(
    *,
    database: pymongo.database.Database,
) -> Optional[dict]:
    # To be idempotent, do not attempt to create if patient already exists
    if scope.database.patients.get_patient_identity(
        database=database,
        patient_id="persistentempty"
    ):
        return

    created_patient = scope.populate.populate_fake.populate_fake_patient_empty(
        database=database,
        patient_id="persistentempty"
    )

    return created_patient


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

        created_patient = {
            "patientId": patient_identity_document[scope.database.patients.PATIENT_IDENTITY_SEMANTIC_SET_ID],
            "name": patient_identity_document["name"],
            "MRN": patient_identity_document["MRN"],
        }

        result.append(created_patient)

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
