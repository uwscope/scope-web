import copy
import faker as _faker
import pymongo.database

import scope.config
import scope.populate.cognito.populate_cognito
import scope.populate.fake.populate_fake
import scope.populate.patient.populate_patient
import scope.populate.provider.populate_provider


FAKER_INSTANCE = _faker.Faker(locale="la")


def populate_from_config(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    populate_config: dict,
) -> dict:
    """
    Populate from a provided populate config.

    Return new state of populate config.
    """
    populate_config = copy.deepcopy(populate_config)

    #
    # Expand any creation of fake patients and providers,
    # then they are populated using the same scripts as "real" patients and providers.
    #
    populate_config = scope.populate.fake.populate_fake.populate_fake_config(
        faker_factory=FAKER_INSTANCE,
        populate_config=populate_config,
    )

    #
    # Execute population of patients
    #
    populate_config = _populate_patients_from_config(
        database=database,
        cognito_config=cognito_config,
        populate_config=populate_config,
    )

    #
    # Execute population of providers
    #
    populate_config = _populate_providers_from_config(
        database=database,
        cognito_config=cognito_config,
        populate_config=populate_config,
    )

    return populate_config


def _populate_patients_from_config(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    populate_config: dict,
) -> dict:
    populate_config = copy.deepcopy(populate_config)

    #
    # Create specified patients
    #
    created_patients = scope.populate.patient.populate_patient.create_patients_from_configs(
        database=database,
        create_patient_configs=populate_config["patients"]["create"],
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
            ] = scope.populate.cognito.populate_cognito.populate_account_from_config(
                database=database,
                cognito_config=cognito_config,
                populate_config_account=patient_current["account"],
            )

    #
    # Link patient identities to patient Cognito accounts
    #
    scope.populate.patient.populate_patient.ensure_patient_identities(
        database=database,
        patients=populate_config["patients"]["existing"],
    )

    return populate_config


def _populate_providers_from_config(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    populate_config: dict,
) -> dict:
    populate_config = copy.deepcopy(populate_config)

    #
    # Create specified providers
    #
    created_providers = scope.populate.provider.populate_provider.create_providers(
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
            ] = scope.populate.cognito.populate_cognito.populate_account_from_config(
                database=database,
                cognito_config=cognito_config,
                populate_config_account=provider_current["account"],
            )

    #
    # Link provider identities to provider Cognito accounts
    #
    scope.populate.provider.populate_provider.ensure_provider_identities(
        database=database,
        providers=populate_config["providers"]["existing"],
    )

    return populate_config
