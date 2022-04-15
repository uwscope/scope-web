import boto3
import pymongo.database
from typing import List, Optional

import scope.config
from scope.populate.cognito import generate_temporary_password
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.schema


ACTION_NAME = "reset_cognito_password"


class ResetCognitoPassword(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        # Search for any existing patient who has the desired action pending
        for patient_config_current in populate_config["patients"]["existing"]:
            actions = patient_config_current.get("actions", [])
            if ACTION_NAME in actions:
                return _PatientResetCognitoPasswordAction(
                    patient_id=patient_config_current["patientId"],
                    patient_name=patient_config_current["name"],
                )

        # Search for any existing provider who has the desired action pending
        for provider_config_current in populate_config["providers"]["existing"]:
            actions = provider_config_current.get("actions", [])
            if ACTION_NAME in actions:
                return _ProviderResetCognitoPasswordAction(
                    provider_id=provider_config_current["providerId"],
                    provider_name=provider_config_current["name"],
                )

        return None


class _PatientResetCognitoPasswordAction(PopulateAction):
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
            "Reset Cognito password for '{}' ({})".format(
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
        _reset_cognito_password(
            database=populate_context.database,
            cognito_config=populate_context.cognito_config,
            account_config=patient_config["account"]["existing"],
        )

        return populate_config


class _ProviderResetCognitoPasswordAction(PopulateAction):
    provider_id: str
    provider_name: str

    def __init__(
        self,
        *,
        provider_id: str,
        provider_name: str,
    ):
        self.provider_id = provider_id
        self.provider_name = provider_name

    def prompt(self) -> List[str]:
        return [
            "Reset Cognito password for '{}' ({})".format(
                self.provider_name,
                self.provider_id,
            )
        ]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Get the provider config
        provider_config = None
        for provider_config_current in populate_config["providers"]["existing"]:
            if provider_config_current["providerId"] == self.provider_id:
                provider_config = provider_config_current
                break

        # Confirm we found the provider
        if not provider_config:
            raise ValueError("populate_config was modified")

        # Remove the action from the pending list
        provider_config["actions"].remove(ACTION_NAME)

        # Perform the update
        _reset_cognito_password(
            database=populate_context.database,
            cognito_config=populate_context.cognito_config,
            account_config=provider_config["account"]["existing"],
        )

        return populate_config


def _reset_cognito_password(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    account_config: dict,  # Subset of a patient config or a provider config
) -> None:
    # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    boto_session = boto3.Session()
    boto_userpool = boto_session.client("cognito-idp")

    reset_account_name = account_config["accountName"]
    reset_temporary_password = generate_temporary_password()

    boto_userpool.admin_set_user_password(
        UserPoolId=cognito_config.poolid,
        Username=reset_account_name,
        Password=reset_temporary_password,
        Permanent=False,
    )

    # Put the temporary password in the config
    account_config["temporaryPassword"] = reset_temporary_password
