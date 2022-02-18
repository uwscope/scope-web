"""
This will need to be overhauled as identity is defined.
"""

from typing import Callable

import faker
import pytest
import scope.database.collection_utils as collection_utils
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def fake_identity_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake identity documents.
    """

    def factory() -> dict:
        fake_identity = {
            "_type": "identity",
            "identityId": collection_utils.generate_set_id(),
            "name": faker_factory.name(),
        }

        return fake_identity

    return factory


@pytest.fixture(name="data_fake_identity_factory")
def fixture_data_fake_identity_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_identity_factory.
    """
    unvalidated_factory = fake_identity_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_identity = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.identity_schema,
            document=fake_identity,
        )

        return fake_identity

    return factory
