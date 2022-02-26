from dataclasses import dataclass
import pymongo.database
import pytest
from typing import Callable
from typing import List

import scope.database.providers


@dataclass(frozen=True)
class DatabaseTempProvider:
    provider_id: str
    provider_identity: dict


@pytest.fixture(name="database_temp_provider_factory")
def fixture_database_temp_provider_factory(
    database_client: pymongo.database.Database,
    data_fake_provider_identity_factory: Callable[[], dict],
) -> Callable[[], DatabaseTempProvider]:
    """
    Fixture for database_temp_provider_factory.

    Provides a factory for obtaining a provider.
    Removes any temporary providers that are created by obtained factory.
    """

    # List of providers created by the factory
    temp_providers: List[DatabaseTempProvider] = []

    # Actual factory for obtaining a temporary provider.
    def factory() -> DatabaseTempProvider:
        temp_provider_identity = data_fake_provider_identity_factory()
        temp_provider_identity = scope.database.providers.create_provider(
            database=database_client,
            name=temp_provider_identity["name"],
            role=temp_provider_identity["role"],
        )

        temp_provider = DatabaseTempProvider(
            provider_id=temp_provider_identity["_set_id"],
            provider_identity=temp_provider_identity,
        )

        temp_providers.append(temp_provider)

        return temp_provider

    yield factory

    # Remove any created providers
    for temp_provider_delete in temp_providers:
        scope.database.providers.delete_provider(
            database=database_client,
            provider_id=temp_provider_delete.provider_id,
            destructive=True,
        )
