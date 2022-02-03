import random
from datetime import datetime
from typing import Callable

import faker
import pytest
import scope.database.patient.safety_plan
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils
import scope.testing.fake_data.fixtures_fake_contact

OPTIONAL_PROPERTIES = [
    "lastUpdatedDate",
    "reasonsForLiving",
    "warningSigns",
    "copingStrategies",
    "distractions",
    "supporters",
    "professionalSupporters",
    "urgentServices",
    "safeEnvironment",
]

# TODO: Move this to fake_utils.py if other fixtures need this method.
def generate_contacts(*, faker_factory: faker.Faker) -> list:
    return [
        scope.testing.fake_data.fixtures_fake_contact.fake_contact_factory(
            faker_factory=faker_factory
        )()
        for i in range(0, random.randint(1, 5))
    ]


def fake_safety_plan_factory(
    *, faker_factory: faker.Faker, validate: bool = True
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake patient safety plan documents.
    """

    def factory() -> dict:
        fake_safety_plan = {
            "_type": scope.database.patient.safety_plan.DOCUMENT_TYPE,
            "assigned": fake_utils.fake_boolean_value(),
            "assignedDate": faker_factory.date(),
            "lastUpdatedDate": faker_factory.date(),
            "reasonsForLiving": faker_factory.text(),
            "warningSigns": faker_factory.texts(),
            "copingStrategies": faker_factory.texts(),
            "distractions": faker_factory.texts()
            + generate_contacts(faker_factory=faker_factory),
            "supporters": generate_contacts(faker_factory=faker_factory),
            "professionalSupporters": generate_contacts(faker_factory=faker_factory),
            "urgentServices": generate_contacts(faker_factory=faker_factory),
            "safeEnvironment": faker_factory.texts(),
        }

        # Remove a randomly sampled subset of optional parameters.
        for key in fake_utils.fake_sample_random_values(OPTIONAL_PROPERTIES):
            del fake_safety_plan[key]

        if validate:
            scope.schema.raise_for_invalid(
                schema=scope.schema.safety_plan_schema,
                document=fake_safety_plan,
            )

        return fake_safety_plan

    return factory


@pytest.fixture(name="data_fake_safety_plan_factory")
def fixture_data_fake_safety_plan_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_safety_plan_factory.
    """

    return fake_safety_plan_factory(
        faker_factory=faker,
        validate=True,
    )
