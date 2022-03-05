import copy
import pymongo.database

import scope.database.providers


def create_provider(
    *,
    database: pymongo.database.Database,
    name: str,
    role: str,
    create_provider: dict,
) -> dict:
    # Consistency check
    if not all([
        name == create_provider["name"],
        role == create_provider["role"],
    ]):
        raise ValueError()

    # Create the provider
    provider_identity_document = scope.database.providers.create_provider(
        database=database,
        name=name,
        role=role,
    )

    # Update the populate config object
    created_provider = copy.deepcopy(create_provider)
    created_provider.update({
        "providerId": provider_identity_document[
            scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
        ],
    })

    return created_provider
