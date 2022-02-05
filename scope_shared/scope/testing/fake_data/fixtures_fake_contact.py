import random
from datetime import datetime
from typing import Callable

import faker
import pytest
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_PROPERTIES = [
    "address",
    "phoneNumber",
    "emergencyNumber",
]


def fake_contact_factory(
    *, faker_factory: faker.Faker, validate: bool = True
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake contact documents.
    """

    def factory() -> dict:

        fake_contact = {
            "contactType": fake_utils.fake_enum_value(
                scope.testing.fake_data.enums.ContactType
            ),
            "name": faker_factory.name(),
            "address": faker_factory.address(),
            "phoneNumber": faker_factory.phone_number(),
            "emergencyNumber": faker_factory.phone_number(),
        }

        # Remove a randomly sampled subset of optional parameters.
        for key in fake_utils.fake_sample_random_values(OPTIONAL_PROPERTIES):
            del fake_contact[key]

        if validate:
            scope.schema.raise_for_invalid(
                schema=scope.schema.contact_schema,
                document=fake_contact,
            )

        return fake_contact

    return factory


@pytest.fixture(name="data_fake_contact_factory")
def fixture_data_fake_contact_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_contact_factory.
    """

    return fake_contact_factory(
        faker_factory=faker,
        validate=True,
    )
