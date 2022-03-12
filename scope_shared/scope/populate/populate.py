import copy
import pymongo.database
from typing import List

import scope.config
import scope.populate.populate_account
import scope.populate.populate_fake
import scope.populate.populate_patient
import scope.populate.populate_provider


def populate_from_config(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    populate_config: dict,
) -> dict:
    """
    Populate from a provided config.

    Return a new state of the populate config.
    """
    populate_config = copy.deepcopy(populate_config)

    #
    # Create any fake patients and providers
    #
    populate_config = scope.populate.populate_fake.populate_fake_from_config(
        database=database,
        populate_config=populate_config,
    )

    #
    # Create specified patients
    #
    created_patients = scope.populate.populate_patient.create_patients(
        database=database,
        create_patients=populate_config["patients"]["create"],
    )
    populate_config["patients"]["create"] = []
    populate_config["patients"]["existing"].extend(created_patients)

    #
    # Populate patient Cognito accounts
    #
    for patient_current in populate_config["patients"]["existing"]:
        if "account" in patient_current:
            patient_current[
                "account"
            ] = scope.populate.populate_account.populate_account_from_config(
                database=database,
                cognito_config=cognito_config,
                populate_config_account=patient_current["account"],
            )

    #
    # Link patient identities to patient Cognito accounts
    #
    scope.populate.populate_patient.ensure_patient_identities(
        database=database,
        patients=populate_config["patients"]["existing"],
    )

    #
    # Create specified providers
    #
    created_providers = scope.populate.populate_provider.create_providers(
        database=database,
        create_providers=populate_config["providers"]["create"],
    )
    populate_config["providers"]["create"] = []
    populate_config["providers"]["existing"].extend(created_providers)

    #
    # Populate provider Cognito accounts
    #
    for provider_current in populate_config["providers"]["existing"]:
        if "account" in provider_current:
            provider_current[
                "account"
            ] = scope.populate.populate_account.populate_account_from_config(
                database=database,
                cognito_config=cognito_config,
                populate_config_account=provider_current["account"],
            )

    #
    # Link provider identities to provider Cognito accounts
    #
    scope.populate.populate_provider.ensure_provider_identities(
        database=database,
        providers=populate_config["providers"]["existing"],
    )

    return populate_config
