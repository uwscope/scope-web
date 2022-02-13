import random
from typing import Callable

import faker
import pytest
import scope.database.document_utils as document_utils
import scope.database.format_utils as format_utils
import scope.database.patient.safety_plan
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS = [
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


def fake_safety_plan_factory(
    *,
    faker_factory: faker.Faker,
    fake_contact_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake safety plan documents.
    """

    def factory() -> dict:
        distractions = []
        distractions.extend(faker_factory.texts(nb_texts=random.randint(1, 5)))
        distractions.extend(
            [fake_contact_factory() for _ in range(random.randint(1, 5))]
        )
        random.shuffle(distractions)

        fake_safety_plan = {
            "_type": scope.database.patient.safety_plan.DOCUMENT_TYPE,
            "assigned": random.choice([True, False]),
            "assignedDate": format_utils.format_date(
                faker_factory.date_object()
            ),
            "lastUpdatedDate": format_utils.format_date(
                faker_factory.date_object()
            ),
            "reasonsForLiving": faker_factory.text(),
            "warningSigns": faker_factory.texts(nb_texts=random.randint(1, 5)),
            "copingStrategies": faker_factory.texts(nb_texts=random.randint(1, 5)),
            "distractions": distractions,
            "supporters": [
                fake_contact_factory() for _ in range(random.randint(1, 5))
            ],
            "professionalSupporters": [
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

        return document_utils.normalize_document(document=fake_safety_plan)

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

        fake_utils.xfail_for_invalid(
            schema=scope.schema.safety_plan_schema,
            document=fake_safety_plan,
        )

        return fake_safety_plan

    return factory
