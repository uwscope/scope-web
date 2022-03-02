import pymongo.database
from typing import List

import scope.database.patients
import scope.database.providers


def populate_from_config(
    *,
    database: pymongo.database.Database,
    populate_config: dict
) -> dict:
    """
    Populate from a provided config.

    Return a new state of the populate config.
    """

    created_providers = _create_providers(
        database=database,
        create_providers=populate_config["providers"]["create"],
    )
    populate_config["providers"]["create"] = []
    populate_config["providers"]["existing"].extend(created_providers)

    return populate_config


def _create_providers(
    *,
    database: pymongo.database.Database,
    create_providers: List[dict],
) -> List[dict]:
    created_providers: List[dict] = []
    for create_provider_current in create_providers:
        provider_identity_document = scope.database.providers.create_provider(
            database=database,
            name=create_provider_current["name"],
            role=create_provider_current["role"],
        )

        created_provider = {
            "providerId": provider_identity_document[scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID],
            "name": provider_identity_document["name"],
            "role": provider_identity_document["role"],
        }

        created_providers.append(created_provider)

    return created_providers
