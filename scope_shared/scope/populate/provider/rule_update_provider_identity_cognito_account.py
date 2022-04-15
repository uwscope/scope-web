import copy
import pymongo.database
from typing import List, Optional

import scope.database.providers
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.schema
import scope.schema_utils as schema_utils

ACTION_NAME = "update_provider_identity_cognito_account"


class UpdateProviderIdentityCognitoAccount(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        # Search for any existing provider who has the desired action pending
        for provider_config_current in populate_config["providers"]["existing"]:
            actions = provider_config_current.get("actions", [])
            if ACTION_NAME in actions:
                return _UpdateProviderIdentityCognitoAccountAction(
                    provider_id=provider_config_current["providerId"],
                    provider_name=provider_config_current["name"],
                )

        return None


class _UpdateProviderIdentityCognitoAccountAction(PopulateAction):
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
            "Update provider identity Cognito account for '{}' ({})".format(
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
        _update_provider_identity_cognito_account(
            database=populate_context.database,
            provider_config=provider_config,
        )

        return populate_config


def _update_provider_identity_cognito_account(
    *,
    database: pymongo.database.Database,
    provider_config: dict,
) -> None:
    # Get the provider ID
    provider_id = provider_config["providerId"]

    # Get the provider identity document
    provider_identity_document = scope.database.providers.get_provider_identity(
        database=database,
        provider_id=provider_id,
    )

    # Check whether to trigger an actual update
    trigger_update = False
    if not trigger_update:
        # Trigger update if the Cognito account is missing
        trigger_update = "cognitoAccount" not in provider_identity_document
    if not trigger_update:
        # Trigger update if the cognitoId is incorrect
        trigger_update = (
            provider_identity_document["cognitoAccount"].get("cognitoId", None)
            != provider_config["account"]["existing"]["cognitoId"]
        )
    if not trigger_update:
        # Trigger update if the email is incorrect
        trigger_update = (
            provider_identity_document["cognitoAccount"].get("email", None)
            != provider_config["account"]["existing"]["email"]
        )

    # Perform the update if needed
    if trigger_update:
        provider_identity_document = copy.deepcopy(provider_identity_document)

        del provider_identity_document["_id"]
        provider_identity_document.update(
            {
                "cognitoAccount": {
                    "cognitoId": provider_config["account"]["existing"]["cognitoId"],
                    "email": provider_config["account"]["existing"]["email"],
                }
            }
        )

        # TODO: move into database layer
        schema_utils.raise_for_invalid_schema(
            data=provider_identity_document,
            schema=scope.schema.provider_identity_schema,
        )

        result = scope.database.providers.put_provider_identity(
            database=database,
            provider_id=provider_config["providerId"],
            provider_identity=provider_identity_document,
        )
        if not result.inserted_count == 1:
            raise RuntimeError("put_provider_identity failed")
