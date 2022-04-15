import copy
from typing import List, Optional

import scope.enums
import scope.database.providers
import scope.populate.provider.rule_update_provider_identity_cognito_account
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.testing.fake_data.fixtures_fake_provider_identity


class CreateProvider(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        # If there is any provider to be created, create the first provider.
        # Later steps will use providerId, but that does not yet exist.
        if len(populate_config["providers"]["create"]) > 0:
            return _CreateProviderAction(
                provider_name=populate_config["providers"]["create"][0]["name"]
            )

        return None


class _CreateProviderAction(PopulateAction):
    provider_name: str

    def __init__(
        self,
        *,
        provider_name: str,
    ):
        self.provider_name = provider_name

    def prompt(self) -> List[str]:
        return ["Create provider '{}'".format(self.provider_name)]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Get the provider config
        provider_config = populate_config["providers"]["create"][0]

        # Confirm the provider name matches what we expect
        if provider_config["name"] != self.provider_name:
            raise ValueError("populate_config was modified")

        # Remove the provider from the create list
        del populate_config["providers"]["create"][0]

        # Create the provider
        provider_identity_document = scope.database.providers.create_provider(
            database=populate_context.database,
            name=provider_config["name"],
            role=provider_config["role"],
        )

        # Update the provider config
        provider_config.update(
            {
                "providerId": provider_identity_document[
                    scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
                ],
            }
        )

        # Specify follow-up actions
        actions = provider_config.get("actions", [])

        # New providers with an account must have identity updated for that account.
        # Note the account might not exist yet,
        # but queue up the action and rely on rules to create the account first.
        if "account" in provider_config:
            actions = actions + [
                scope.populate.provider.rule_update_provider_identity_cognito_account.ACTION_NAME
            ]

        # Store the updated actions
        provider_config["actions"] = actions

        # Add the created provider to the config
        populate_config["providers"]["existing"].append(provider_config)

        return populate_config
