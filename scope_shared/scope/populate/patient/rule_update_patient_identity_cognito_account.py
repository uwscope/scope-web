import copy
import pymongo.database
from typing import List, Optional

import scope.database.patients
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.schema
import scope.schema_utils as schema_utils

ACTION_NAME = "update_patient_identity_cognito_account"


class UpdatePatientIdentityCognitoAccount(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        # Search for any existing patient who has the desired action pending
        for patient_config_current in populate_config["patients"]["existing"]:
            if "actions" not in patient_config_current:
                continue
            if ACTION_NAME not in patient_config_current["actions"]:
                continue

            # Must also have an existing account
            if "account" not in patient_config_current:
                continue
            if "existing" not in patient_config_current["account"]:
                continue

            return _UpdatePatientIdentityCognitoAccountAction(
                patient_id=patient_config_current["patientId"],
                patient_name=patient_config_current["name"],
            )

        return None


class _UpdatePatientIdentityCognitoAccountAction(PopulateAction):
    patient_id: str
    patient_name: str

    def __init__(
        self,
        *,
        patient_id: str,
        patient_name: str,
    ):
        self.patient_id = patient_id
        self.patient_name = patient_name

    def prompt(self) -> List[str]:
        return [
            "Update patient identity Cognito account for '{}' ({})".format(
                self.patient_name,
                self.patient_id,
            )
        ]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Get the patient config
        patient_config = None
        for patient_config_current in populate_config["patients"]["existing"]:
            if patient_config_current["patientId"] == self.patient_id:
                patient_config = patient_config_current
                break

        # Confirm we found the patient
        if not patient_config:
            raise ValueError("populate_config was modified")

        # Remove the action from the pending list
        patient_config["actions"].remove(ACTION_NAME)

        # Perform the update
        _update_patient_identity_cognito_account(
            database=populate_context.database,
            patient_config=patient_config,
        )

        return populate_config


def _update_patient_identity_cognito_account(
    *,
    database: pymongo.database.Database,
    patient_config: dict,
) -> None:
    # Get the patient ID
    patient_id = patient_config["patientId"]

    # Get the patient identity document
    patient_identity_document = scope.database.patients.get_patient_identity(
        database=database,
        patient_id=patient_id,
    )

    # Check whether to trigger an actual update
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
            raise RuntimeError("put_patient_identity failed")
