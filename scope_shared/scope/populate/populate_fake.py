import copy
import pymongo.database
from typing import List, Optional

import scope.database.patients
import scope.database.providers
import scope.enums
import scope.populate.populate_fake_patient
import scope.populate.populate_fake_provider


def populate_fake_from_config(
    *,
    database: pymongo.database.Database,
    populate_config: dict,
) -> dict:
    populate_config = copy.deepcopy(populate_config)

    #
    # Create any "persistent" patient
    # Keep this first so this patient sorts first
    #
    if populate_config["patients"].get("create_fake_persistent", False):
        created_patient = _create_fake_persistent_patient(
            database=database,
        )
        del populate_config["patients"]["create_fake_persistent"]

        if created_patient:
            populate_config["patients"]["existing"].append(created_patient)

    #
    # Create any "persistentempty" patient
    #
    if populate_config["patients"].get("create_fake_persistent_empty", False):
        created_patient = _create_fake_persistent_empty_patient(
            database=database,
        )
        del populate_config["patients"]["create_fake_persistent_empty"]

        if created_patient:
            populate_config["patients"]["existing"].append(created_patient)

    #
    # Create any fake patients
    #
    if "create_fake" in populate_config["patients"]:
        created_patients = _create_fake_patients(
            database=database,
            create_fake=populate_config["patients"]["create_fake"],
        )
        del populate_config["patients"]["create_fake"]

        populate_config["patients"]["existing"].extend(created_patients)

    #
    # Create any fake empty patients
    #
    if "create_fake_empty" in populate_config["patients"]:
        created_patients = _create_fake_empty_patients(
            database=database,
            create_fake_empty=populate_config["patients"]["create_fake_empty"],
        )
        del populate_config["patients"]["create_fake_empty"]

        populate_config["patients"]["existing"].extend(created_patients)

    #
    # Create any fake pyschiatrists
    #
    if "create_fake_psychiatrist" in populate_config["providers"]:
        created_providers = _create_fake_providers(
            database=database,
            create_fake=populate_config["providers"]["create_fake_psychiatrist"],
            role=scope.enums.ProviderRole.Psychiatrist.value,
        )
        del populate_config["providers"]["create_fake_psychiatrist"]

        populate_config["providers"]["existing"].extend(created_providers)

    #
    # Create any fake social workers
    #
    if "create_fake_social_worker" in populate_config["providers"]:
        created_providers = _create_fake_providers(
            database=database,
            create_fake=populate_config["providers"]["create_fake_social_worker"],
            role=scope.enums.ProviderRole.SocialWorker.value,
        )
        del populate_config["providers"]["create_fake_social_worker"]

        populate_config["providers"]["existing"].extend(created_providers)

    #
    # Create any fake study staff
    #
    if "create_fake_study_staff" in populate_config["providers"]:
        created_providers = _create_fake_providers(
            database=database,
            create_fake=populate_config["providers"]["create_fake_study_staff"],
            role=scope.enums.ProviderRole.StudyStaff.value,
        )
        del populate_config["providers"]["create_fake_study_staff"]

        populate_config["providers"]["existing"].extend(created_providers)

    return populate_config


def _create_fake_patients(
    *,
    database: pymongo.database.Database,
    create_fake: int,
) -> List[dict]:
    created_patients = []
    for _ in range(create_fake):
        created_patient = scope.populate.populate_fake_patient.populate_fake_patient(
            database=database,
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
        created_patient = (
            scope.populate.populate_fake_patient.populate_fake_patient_empty(
                database=database
            )
        )
        created_patients.append(created_patient)

    return created_patients


def _create_fake_persistent_patient(
    *,
    database: pymongo.database.Database,
) -> Optional[dict]:
    # To be idempotent, do not attempt to create if patient already exists
    if scope.database.patients.get_patient_identity(
        database=database,
        patient_id="persistent",
    ):
        return

    created_patient = scope.populate.populate_fake_patient.populate_fake_patient(
        database=database,
        patient_id="persistent",
    )

    return created_patient


def _create_fake_persistent_empty_patient(
    *,
    database: pymongo.database.Database,
) -> Optional[dict]:
    # To be idempotent, do not attempt to create if patient already exists
    if scope.database.patients.get_patient_identity(
        database=database,
        patient_id="persistentempty",
    ):
        return

    created_patient = scope.populate.populate_fake_patient.populate_fake_patient_empty(
        database=database,
        patient_id="persistentempty",
    )

    return created_patient


def _create_fake_providers(
    *,
    database: pymongo.database.Database,
    create_fake: int,
    role: str,
) -> List[dict]:
    created_providers = []
    for _ in range(create_fake):
        created_provider = scope.populate.populate_fake_provider.populate_fake_provider(
            database=database,
            role=role,
        )
        created_providers.append(created_provider)

    return created_providers
