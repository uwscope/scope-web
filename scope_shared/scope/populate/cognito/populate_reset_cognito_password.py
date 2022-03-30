import boto3
import copy
import pymongo.database

import scope.config
import scope.database.patients
import scope.schema
import scope.schema_utils as schema_utils

from scope.populate.cognito.populate_cognito import _generate_temporary_password as generate_temporary_password

ACTION_NAME = "reset_cognito_password"


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

    if "account" not in patient_config:
        raise ValueError('patient_config["account"] not found', patient_config)
    if "existing" not in patient_config["account"]:
        raise ValueError('patient_config["account"]["existing"] not found')
    if "cognitoId" not in patient_config["account"]["existing"]:
        raise ValueError(
            'patient_config["account"]["existing"]["cognitoId"] not found',
            patient_config,
        )


def reset_cognito_password(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    patient_config: dict,
) -> dict:
    # Ensure a valid setup
    _ensure_valid(patient_config=patient_config)

    # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    boto_session = boto3.Session()
    boto_userpool = boto_session.client("cognito-idp")

    reset_account_name = patient_config["account"]["existing"]["accountName"]
    reset_temporary_password = generate_temporary_password()

    boto_userpool.admin_set_user_password(
        UserPoolId=cognito_config.poolid,
        Username=reset_account_name,
        Password=reset_temporary_password,
        Permanent=False,
    )

    # Update the config
    updated_patient_config = copy.deepcopy(patient_config)

    # Put the temporary password in the config
    updated_patient_config["account"]["existing"]["temporaryPassword"] = reset_temporary_password

    # Mark the action complete
    updated_patient_config["actions"].remove(ACTION_NAME)

    return updated_patient_config
