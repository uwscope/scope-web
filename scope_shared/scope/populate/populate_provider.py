import copy
import pymongo.database
from typing import List

import scope.database.providers
import scope.schema
import scope.schema_utils


def create_providers(
    *,
    database: pymongo.database.Database,
    create_providers: List[dict],
) -> List[dict]:
    result: List[dict] = []
    for create_provider_current in create_providers:
        created_provider = _create_provider(
            database=database,
            name=create_provider_current["name"],
            role=create_provider_current["role"],
            create_provider=create_provider_current,
        )

        result.append(created_provider)

    return result


def _create_provider(
    *,
    database: pymongo.database.Database,
    name: str,
    role: str,
    create_provider: dict,
) -> dict:
    # Consistency check
    if not all(
        [
            name == create_provider["name"],
            role == create_provider["role"],
        ]
    ):
        raise ValueError()

    # Create the provider
    provider_identity_document = scope.database.providers.create_provider(
        database=database,
        name=name,
        role=role,
    )

    # Update the provider object
    created_provider = copy.deepcopy(create_provider)
    created_provider.update(
        {
            "providerId": provider_identity_document[
                scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
            ],
        }
    )

    return created_provider


def ensure_provider_identities(
    *,
    database: pymongo.database.Database,
    providers: List[dict],
) -> None:
    for provider_current in providers:
        # Consistency check:
        # - Should only be called with existing providers
        # - All providers should include providerId per schema
        if not all(
            [
                "providerId" in provider_current,
            ]
        ):
            raise ValueError()

        # Only ensure identities for providers that have an account
        if "account" in provider_current:
            _ensure_provider_identity(database=database, provider=provider_current)


def _ensure_provider_identity(
    *,
    database: pymongo.database.Database,
    provider: dict,
) -> None:
    # Consistency check:
    # - Should only be called for providers with an account
    # - Should only be called after account creation
    # - Account should include cognitoId and email per schema
    if not all(
        [
            "account" in provider,
            "create" not in provider["account"],
            "existing" in provider["account"],
            "cognitoId" in provider["account"]["existing"],
            "email" in provider["account"]["existing"],
        ]
    ):
        raise ValueError()

    provider_identity_document = scope.database.providers.get_provider_identity(
        database=database,
        provider_id=provider["providerId"],
    )

    # Check for a need to update the identity document
    update_identity_document = False
    if not update_identity_document:
        update_identity_document = "cognitoAccount" not in provider_identity_document
    if not update_identity_document:
        update_identity_document = (
            provider_identity_document["cognitoAccount"]["cognitoId"]
            != provider["account"]["existing"]["cognitoId"]
        )
    if not update_identity_document:
        update_identity_document = (
            provider_identity_document["cognitoAccount"]["email"]
            != provider["account"]["existing"]["email"]
        )

    # Perform the update if needed
    if update_identity_document:
        provider_identity_document = copy.deepcopy(provider_identity_document)

        del provider_identity_document["_id"]
        provider_identity_document.update(
            {
                "cognitoAccount": {
                    "cognitoId": provider["account"]["existing"]["cognitoId"],
                    "email": provider["account"]["existing"]["email"],
                }
            }
        )

        scope.schema_utils.raise_for_invalid_schema(
            data=provider_identity_document,
            schema=scope.schema.provider_identity_schema,
        )

        result = scope.database.providers.put_provider_identity(
            database=database,
            provider_id=provider["providerId"],
            provider_identity=provider_identity_document,
        )
        if not result.inserted_count == 1:
            raise RuntimeError()
