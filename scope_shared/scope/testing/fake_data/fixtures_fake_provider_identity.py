from typing import Callable

import faker
import pytest
import scope.database.collection_utils as collection_utils
import scope.database.providers
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_provider_identity_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake provider identity documents.
    """

    def factory() -> dict:
        fake_identity = {
            "_type": scope.database.providers.PROVIDER_IDENTITY_DOCUMENT_TYPE,
            "name": faker_factory.name(),
            "role": fake_utils.fake_enum_value(scope.enums.ProviderRole),
        }

        return fake_identity

    return factory


@pytest.fixture(name="data_fake_provider_identity_factory")
def fixture_data_fake_provider_identity_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_provider_identity_factory.
    """
    unvalidated_factory = fake_provider_identity_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_identity = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.provider_identity_schema,
            data=fake_identity,
        )

        return fake_identity

    return factory
