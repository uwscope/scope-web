import copy
import pymongo.database

import scope.database.patients
import scope.schema
import scope.schema_utils as schema_utils

ACTION_NAME = "update_identity_cognito_account_from_config"


def _ensure_valid(
    *,
    patient_config: dict,
) -> None:
    if "actions" not in patient_config:
        raise ValueError('patient_config["actions"] not found', patient_config)
    if ACTION_NAME not in patient_config["actions"]:
        raise ValueError('ACTION_NAME not found in patient_config["actions"]', patient_config)

    if "account" not in patient_config:
        raise ValueError('patient_config["account"] not found', patient_config)
    if "existing" not in patient_config["account"]:
        raise ValueError('patient_config["account"]["existing"] not found')
    if "cognitoId" not in patient_config["account"]["existing"]:
        raise ValueError('patient_config["account"]["existing"]["cognitoId"] not found', patient_config)
    if "email" not in patient_config["account"]["existing"]:
        raise ValueError('patient_config["account"]["existing"]["email"] not found', patient_config)


def update_identity_cognito_account_from_config(
    *,
    database: pymongo.database.Database,
    patient_config: dict,
) -> dict:
    patient_config = copy.deepcopy(patient_config)

    # Ensure a valid setup
    _ensure_valid(patient_config=patient_config)

    # Get the current identity document
    patient_identity_document = scope.database.patients.get_patient_identity(
        database=database,
        patient_id=patient_config["patientId"],
    )

    # Check whether trigger an actual update
    trigger_update = False
    if not trigger_update:
        # Trigger update if the Cognito account is missing
        trigger_update = "cognitoAccount" not in patient_identity_document
    if not trigger_update:
        # Trigger update if the cognitoId is incorrect
        trigger_update = (
            patient_identity_document["cognitoAccount"].get("cognitoId", None)
            != patient_config["account"]["existing"]["cognitoId"]
        )
    if not trigger_update:
        # Trigger update if the email is incorrect
        trigger_update = (
            patient_identity_document["cognitoAccount"].get("email", None)
            != patient_config["account"]["existing"]["email"]
        )

    # Perform the update if needed
    if trigger_update:
        patient_identity_document = copy.deepcopy(patient_identity_document)

        del patient_identity_document["_id"]
        patient_identity_document.update(
            {
                "cognitoAccount": {
                    "cognitoId": patient_config["account"]["existing"]["cognitoId"],
                    "email": patient_config["account"]["existing"]["email"],
                }
            }
        )

        # TODO: move into database layer
        schema_utils.raise_for_invalid_schema(
            data=patient_identity_document,
            schema=scope.schema.patient_identity_schema,
        )

        result = scope.database.patients.put_patient_identity(
            database=database,
            patient_id=patient_config["patientId"],
            patient_identity=patient_identity_document,
        )
        if not result.inserted_count == 1:
            raise RuntimeError()

    patient_config["actions"].remove(ACTION_NAME)

    return patient_config
