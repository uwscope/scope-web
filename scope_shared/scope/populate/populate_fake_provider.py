import faker
import pymongo.database
from typing import Optional

import scope.database.providers
import scope.testing.fake_data.fixtures_fake_provider_identity


def _create_faker_factory(faker_factory: Optional[faker.Faker]):
    if faker_factory:
        return faker_factory
    else:
        return faker.Faker(locale="la")


def populate_fake_provider(
    *,
    faker_factory: faker.Faker = None,
    database: pymongo.database.Database,
    role: str,
) -> dict:
    faker_factory = _create_faker_factory(faker_factory)

    # Obtain a fake profile
    fake_provider_identity_factory = scope.testing.fake_data.fixtures_fake_provider_identity.fake_provider_identity_factory(
        faker_factory=faker_factory,
    )
    fake_provider_identity = fake_provider_identity_factory()

    # Create the fake provider
    fake_provider_identity = scope.database.providers.create_provider(
        database=database,
        name=fake_provider_identity["name"],
        role=role,
    )

    # Construct the populate config object
    created_provider = {
        "providerId": fake_provider_identity[
            scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
        ],
        "name": fake_provider_identity["name"],
        "role": fake_provider_identity["role"],
    }

    return created_provider
