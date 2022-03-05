import faker
import random
import pytest
import pytz
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.safety_plan
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS = [
    "lastUpdatedDateTime",
    "reasonsForLiving",
    "warningSigns",
    "copingStrategies",
    "socialDistractions",
    "settingDistractions",
    "supporters",
    "professionals",
    "urgentServices",
    "safeEnvironment",
]


def fake_safety_plan_factory(
    *,
    faker_factory: faker.Faker,
    fake_contact_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake safety plan documents.
    """

    def factory() -> dict:
        fake_safety_plan = {
            "_type": scope.database.patient.safety_plan.DOCUMENT_TYPE,
            "assigned": random.choice([True, False]),
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(faker_factory.date_time())
            ),
            "lastUpdatedDateTime": date_utils.format_datetime(
                pytz.utc.localize(faker_factory.date_time())
            ),
            "reasonsForLiving": faker_factory.text(),
            "warningSigns": faker_factory.texts(nb_texts=random.randint(1, 5)),
            "copingStrategies": faker_factory.texts(nb_texts=random.randint(1, 5)),
            "socialDistractions": [
                fake_contact_factory() for _ in range(random.randint(1, 5))
            ],
            "settingDistractions": faker_factory.texts(nb_texts=random.randint(1, 5)),
            "supporters": [fake_contact_factory() for _ in range(random.randint(1, 5))],
            "professionals": [
                fake_contact_factory() for _ in range(random.randint(1, 5))
            ],
            "urgentServices": [
                fake_contact_factory() for _ in range(random.randint(1, 5))
            ],
            "safeEnvironment": faker_factory.texts(nb_texts=random.randint(1, 5)),
        }

        # Remove a randomly sampled subset of optional parameters.
        fake_safety_plan = fake_utils.fake_optional(
            document=fake_safety_plan,
            optional_keys=OPTIONAL_KEYS,
        )

        return fake_safety_plan

    return factory


@pytest.fixture(name="data_fake_safety_plan_factory")
def fixture_data_fake_safety_plan_factory(
    faker: faker.Faker,
    data_fake_contact_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_safety_plan_factory.
    """

    unvalidated_factory = fake_safety_plan_factory(
        faker_factory=faker,
        fake_contact_factory=data_fake_contact_factory,
    )

    def factory() -> dict:
        fake_safety_plan = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.safety_plan_schema,
            data=fake_safety_plan,
        )

        return fake_safety_plan

    return factory
