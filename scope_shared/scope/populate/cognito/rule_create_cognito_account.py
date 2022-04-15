import boto3
from typing import List, Optional

import scope.config
from scope.populate.cognito import generate_temporary_password
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.schema


class CreateCognitoAccount(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        # Search for any existing patient who needs an account created
        for patient_config_current in populate_config["patients"]["existing"]:
            if "account" not in patient_config_current:
                continue
            if "create" not in patient_config_current["account"]:
                continue

            return _PatientCreateCognitoAccountAction(
                patient_id=patient_config_current["patientId"],
                patient_name=patient_config_current["name"],
            )

        # Search for any existing provider who needs an account created
        for provider_config_current in populate_config["providers"]["existing"]:
            if "account" not in provider_config_current:
                continue
            if "create" not in provider_config_current["account"]:
                continue

            return _ProviderCreateCognitoAccountAction(
                provider_id=provider_config_current["providerId"],
                provider_name=provider_config_current["name"],
            )

        return None


class _PatientCreateCognitoAccountAction(PopulateAction):
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
            "Create Cognito account for '{}' ({})".format(
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

        # Perform the account creation
        patient_config["account"]["existing"] = _create_cognito_account(
            cognito_config=populate_context.cognito_config,
            account_config=patient_config["account"]["create"],
        )

        # Remove the account creation request
        del patient_config["account"]["create"]

        return populate_config


class _ProviderCreateCognitoAccountAction(PopulateAction):
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
            "Create Cognito account for '{}' ({})".format(
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

        # Perform the account creation
        provider_config["account"]["existing"] = _create_cognito_account(
            cognito_config=populate_context.cognito_config,
            account_config=provider_config["account"]["create"],
        )

        # Remove the account creation request
        del provider_config["account"]["create"]

        return populate_config


def _get_existing_cognito_users(
    *,
    boto_userpool,
    cognito_config: scope.config.CognitoClientConfig,
) -> List[dict]:
    """
    Obtain a complete list of existing Cognito users.
    """

    user_paginator = boto_userpool.get_paginator("list_users")
    user_pages = user_paginator.paginate(UserPoolId=cognito_config.poolid)

    users = []
    for user_page_current in user_pages:
        users.extend(user_page_current.get("Users", []))

    return users


def _create_cognito_account(
    *,
    cognito_config: scope.config.CognitoClientConfig,
    account_config: dict,  # Subset of a patient config or a provider config
) -> dict:
    # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    boto_session = boto3.Session()
    boto_userpool = boto_session.client("cognito-idp")

    # Account and email address we intend to create
    create_account_name = account_config["accountName"]
    create_email = account_config["email"]
    create_temporary_password = generate_temporary_password()

    # Raise if an account with the same name already exists
    cognito_users_existing = _get_existing_cognito_users(
        boto_userpool=boto_userpool,
        cognito_config=cognito_config,
    )
    for cognito_user_current in cognito_users_existing:
        if cognito_user_current["Username"] == create_account_name:
            raise ValueError(
                'Cognito username "{}" already exists.'.format(create_account_name)
            )

    # Create an account
    response = boto_userpool.admin_create_user(
        UserPoolId=cognito_config.poolid,
        Username=create_account_name,
        TemporaryPassword=create_temporary_password,
        MessageAction="SUPPRESS",
        UserAttributes=[
            {
                "Name": "email",
                "Value": create_email,
            },
            {
                "Name": "email_verified",
                "Value": "True",
            },
        ],
    )

    # If no exception was raised, the account was created.
    # Recover the "sub" user attribute as the associated unique id.
    created_attributes = {
        attribute["Name"]: attribute["Value"]
        for attribute in response["User"]["Attributes"]
    }
    created_cognito_id = created_attributes["sub"]

    # Update the config
    account_config["temporaryPassword"] = create_temporary_password
    account_config["cognitoId"] = created_cognito_id

    return account_config
