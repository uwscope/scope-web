import boto3
import copy
from typing import List, Optional

import scope.config
import scope.database.patients
import scope.database.providers
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.schema


ACTION_NAME = "update_cognito_email"


class UpdateCognitoEmail(PopulateRule):
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
                return _PatientUpdateCognitoEmailAction(
                    patient_id=patient_config_current["patientId"],
                    patient_name=patient_config_current["name"],
                )

        # Search for any existing provider who has the desired action pending
        for provider_config_current in populate_config["providers"]["existing"]:
            actions = provider_config_current.get("actions", [])
            if ACTION_NAME in actions:
                return _ProviderUpdateCognitoEmailAction(
                    provider_id=provider_config_current["providerId"],
                    provider_name=provider_config_current["name"],
                )

        return None


class _PatientUpdateCognitoEmailAction(PopulateAction):
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
            "Update Cognito email for '{}' ({})".format(
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

        # Perform the Cognito update
        _update_cognito_email(
            cognito_config=populate_context.cognito_config,
            account_config=patient_config["account"]["existing"],
        )

        # And update the identity document
        patient_id = patient_config["patientId"]
        patient_identity_document = scope.database.patients.get_patient_identity(
            database=populate_context.database,
            patient_id=patient_id,
        )

        # It is possible the email already matches
        email_current = patient_identity_document["cognitoAccount"]["email"]
        update_email = patient_config["account"]["existing"]["email"]
        if email_current != update_email:
            patient_identity_document = copy.deepcopy(patient_identity_document)
            del patient_identity_document["_id"]

            patient_identity_document["cognitoAccount"]["email"] = update_email

            scope.database.patients.put_patient_identity(
                database=populate_context.database,
                patient_id=patient_id,
                patient_identity=patient_identity_document,
            )

        return populate_config


class _ProviderUpdateCognitoEmailAction(PopulateAction):
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
            "Update Cognito email for '{}' ({})".format(
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

        # Perform the Cognito update
        _update_cognito_email(
            cognito_config=populate_context.cognito_config,
            account_config=provider_config["account"]["existing"],
        )

        # And update the identity document
        provider_id = provider_config["providerId"]
        provider_identity_document = scope.database.providers.get_provider_identity(
            database=populate_context.database,
            provider_id=provider_id,
        )

        # It is possible the email already matches
        email_current = provider_identity_document["cognitoAccount"]["email"]
        update_email = provider_config["account"]["existing"]["email"]
        if email_current != update_email:
            provider_identity_document = copy.deepcopy(provider_identity_document)
            del provider_identity_document["_id"]

            provider_identity_document["cognitoAccount"]["email"] = update_email

            scope.database.providers.put_provider_identity(
                database=populate_context.database,
                provider_id=provider_id,
                provider_identity=provider_identity_document,
            )

        return populate_config


def _update_cognito_email(
    *,
    cognito_config: scope.config.CognitoClientConfig,
    account_config: dict,  # Subset of a patient config or a provider config
) -> None:
    # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    boto_session = boto3.Session()
    boto_userpool = boto_session.client("cognito-idp")

    update_account_name = account_config["accountName"]
    update_email = account_config["email"]

    cognito_user_current = boto_userpool.admin_get_user(
        UserPoolId=cognito_config.poolid,
        Username=update_account_name,
    )

    email_current = None
    for attribute_current in cognito_user_current["UserAttributes"]:
        if attribute_current["Name"] == "email":
            email_current = attribute_current["Value"]
            break

    # It is possible the email already matches
    if email_current != update_email:
        boto_userpool.admin_update_user_attributes(
            UserPoolId=cognito_config.poolid,
            Username=update_account_name,
            UserAttributes=[
                {
                    "Name": "email",
                    "Value": update_email,
                },
                {
                    "Name": "email_verified",
                    "Value": "True",
                },
            ],
        )
