import faker
import pytest
import random
from typing import Callable, List

import scope.database.format_utils
import scope.database.patient.patient_profile
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS = [
    "values",
]


def _fake_value(
    *,
    faker_factory: faker.Faker,
    life_areas: List[dict],  # Life areas will be sampled from this
) -> dict:
    return {
        "id": "WHAT IS THIS",
        "name": faker_factory.text(),
        "dateCreated": scope.database.format_utils.format_date(faker_factory.date_object()),
        "dateEdited": scope.database.format_utils.format_date(faker_factory.date_object()),
        "lifeareaId": random.choice(life_areas)["id"],
        "activities": [
            {
                "id": "id",
                "name": "name",
                "valueId": "",
                "dateCreated": "",
                "dateEdited": "",
                "lifeareaId": "",
            },
            {
                "id": "id",
                "name": "name",
                "valueId": "",
                "dateCreated": "",
                "dateEdited": "",
                "lifeareaId": "",
            },
        ],
    }


def fake_values_inventory_factory(
    *,
    faker_factory: faker.Faker,
    life_areas: List[dict],  # Life areas will be sampled from this
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake value inventory documents.
    """

    def factory() -> dict:
        fake_values_inventory = {
            "_type": "valuesInventory",
            "assigned": random.choice([True, False]),
            "assignedDate": scope.database.format_utils.format_date(faker_factory.date_object()),
            "values": [
                _fake_value(
                    faker_factory=faker_factory,
                    life_areas=life_areas,
                ) for count in range(random.randint(1, 5))
            ],
        }

        # Remove a randomly sampled subset of optional parameters.
        fake_values_inventory = scope.testing.fake_data.fake_utils.fake_optional(
            document=fake_values_inventory,
            optional_keys=OPTIONAL_KEYS,
        )

        return fake_values_inventory

    return factory


@pytest.fixture(name="data_fake_values_inventory_factory")
def fixture_data_fake_values_inventory_factory(
    *,
    faker: faker.Faker,
    data_fake_life_areas: List[dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_values_inventory_factory.
    """

    unvalidated_factory = fake_values_inventory_factory(
        faker_factory=faker,
        life_areas=data_fake_life_areas,
    )

    def factory() -> dict:
        fake_values_inventory = unvalidated_factory()

        scope.testing.fake_data.fake_utils.xfail_for_invalid(
            schema=scope.schema.values_inventory_schema,
            document=fake_values_inventory,
        )

        return fake_values_inventory

    return factory
