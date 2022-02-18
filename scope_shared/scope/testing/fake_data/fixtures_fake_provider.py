"""
This can be removed if we make fixtures_fake_identity.py configurable.
"""

from typing import Callable

import faker
import pytest
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def fake_provider_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake provider documents.
    """

    def factory() -> dict:
        fake_provider = {
            # TODO: Pass identity type as an argument to be able to generate specific identity.
            "_type": fake_utils.fake_enum_value(
                scope.testing.fake_data.enums.ProviderIdentityType
            ),
            "identityId": fake_utils.fake_unique_id(),
            "name": faker_factory.name(),
        }

        return fake_provider

    return factory


@pytest.fixture(name="data_fake_provider_factory")
def fixture_data_fake_provider_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_provider_factory.
    """
    unvalidated_factory = fake_provider_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_provider = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.identity_schema,
            document=fake_provider,
        )

        return fake_provider

    return factory