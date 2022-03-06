import copy
import pymongo.database
from typing import List

import scope.database.providers


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

    # Update the provider object
    created_provider = copy.deepcopy(create_provider)
    created_provider.update({
        "providerId": provider_identity_document[
            scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
        ],
    })

    return created_provider
