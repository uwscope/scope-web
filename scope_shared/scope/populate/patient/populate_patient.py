import copy
import pymongo.database
from typing import List

import scope.config
import scope.database.patients
import scope.populate.cognito.populate_cognito
import scope.populate.patient.create_patient
import scope.populate.patient.update_identity_cognito_account_from_config
import scope.schema
import scope.schema_utils


def populate_patients_from_config(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    populate_config: dict,
) -> dict:
    populate_config = copy.deepcopy(populate_config)

    #
    # Create specified patients
    #
    created_patient_configs = (
        scope.populate.patient.create_patient.create_patients_from_configs(
            database=database,
            create_patient_configs=populate_config["patients"]["create"],
        )
    )
    populate_config["patients"]["create"] = []
    populate_config["patients"]["existing"].extend(created_patient_configs)

    #
    # Apply populate actions to each patient
    #
    for patient_config_current in populate_config["patients"]["existing"]:
        #
        #
        #
        if "account" in patient_config_current:
            patient_config_current[
                "account"
            ] = scope.populate.cognito.populate_cognito.populate_account_from_config(
                database=database,
                cognito_config=cognito_config,
                populate_config_account=patient_config_current["account"],
            )

        #
        # Update patient identity based on account config containing Cognito account
        #
        if scope.populate.patient.update_identity_document_from_account_config.ACTION_NAME in patient_config_current.get("actions", []):
            scope.populate.patient.update_identity_document_from_account_config.update_identity_document_from_account_config(
                database=database,
                patient_config=patient_config_current,
            )

    return populate_config
