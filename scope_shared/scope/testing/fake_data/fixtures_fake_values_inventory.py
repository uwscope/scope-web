import faker
import pytest
import random
from typing import Callable, List

import scope.database.format_utils as format_utils
import scope.database.patient.patient_profile
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS_VALUES_INVENTORY = [
    "lastUpdatedDateTime",
    "values",
]


def _fake_activity(
    *,
    faker_factory: faker.Faker,
) -> dict:
    """
    This is currently tested by inclusion in the values inventory schema.
    If moved out on its own, it should probably get its own tests.
    """

    fake_activity = {
        "name": faker_factory.text(),
        "createdDateTime": format_utils.format_date(faker_factory.date_time()),
        "editedDateTime": format_utils.format_date(faker_factory.date_time()),
        "enjoyment": random.randint(1, 10),
        "importance": random.randint(1, 10),
    }

    return fake_activity


def _fake_value(
    *,
    faker_factory: faker.Faker,
    fake_life_area: dict,  # lifeareaId will be taken from this
) -> dict:
    """
    This is currently tested by inclusion in the values inventory schema.
    If moved out on its own, it should probably get its own tests.

    Although patients may be asked to populate these,
    ensure functionality even if they are not yet populated.
    """

    return {
        "name": faker_factory.text(),
        "createdDateTime": format_utils.format_date(faker_factory.date_time()),
        "editedDateTime": format_utils.format_date(faker_factory.date_time()),
        "lifeareaId": fake_life_area["id"],
        "activities": [
            _fake_activity(
                faker_factory=faker_factory,
            )
            for _ in range(0, 5)
        ],
    }


def fake_values_inventory_factory(
    *,
    faker_factory: faker.Faker,
    fake_life_areas: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake value inventory documents.

    Although patients may be asked to populate these,
    ensure functionality even if they are not yet populated.
    """

    def factory() -> dict:
        fake_values_inventory = {
            "_type": "valuesInventory",
            "assigned": random.choice([True, False]),
            "assignedDateTime": format_utils.format_date(faker_factory.date_time()),
            "lastUpdatedDateTime": format_utils.format_date(faker_factory.date_time()),
            "values": [
                _fake_value(
                    faker_factory=faker_factory,
                    fake_life_area=fake_life_area,
                )
                for fake_life_area in fake_life_areas
                for _ in range(random.randint(0, 5))
            ],
        }

        # Remove a randomly sampled subset of optional parameters.
        fake_values_inventory = fake_utils.fake_optional(
            document=fake_values_inventory,
            optional_keys=OPTIONAL_KEYS_VALUES_INVENTORY,
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
        fake_life_areas=data_fake_life_areas,
    )

    def factory() -> dict:
        fake_values_inventory = unvalidated_factory()

        scope.testing.fake_data.fake_utils.xfail_for_invalid(
            schema=scope.schema.values_inventory_schema,
            document=fake_values_inventory,
        )

        return fake_values_inventory

    return factory


@pytest.fixture(name="data_fake_values_inventory")
def fixture_data_fake_values_inventory(
    *,
    data_fake_values_inventory_factory: Callable[[], dict],
) -> dict:
    """
    Fixture for data_fake_values_inventory.
    """

    return data_fake_values_inventory_factory()
