import faker
import pytest
import pytz
import random
from typing import Callable, List

import scope.database.date_utils as date_utils
import scope.database.patient.patient_profile
import scope.enums
import scope.schema
import scope.schema_utils
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
        "createdDateTime": date_utils.format_datetime(
            pytz.utc.localize(faker_factory.date_time())
        ),
        "editedDateTime": date_utils.format_datetime(
            pytz.utc.localize(faker_factory.date_time())
        ),
        "enjoyment": random.randint(1, 10),
        "importance": random.randint(1, 10),
    }

    return fake_activity


def _fake_value(
    *,
    faker_factory: faker.Faker,
    life_area: dict,
) -> dict:
    """
    This is currently tested by inclusion in the values inventory schema.
    If moved out on its own, it should probably get its own tests.

    Although patients will be asked to populate these,
    ensure functionality even if they are not yet populated.
    """

    return {
        "name": faker_factory.text(),
        "createdDateTime": date_utils.format_datetime(
            pytz.utc.localize(faker_factory.date_time())
        ),
        "editedDateTime": date_utils.format_datetime(
            pytz.utc.localize(faker_factory.date_time())
        ),
        "lifeareaId": life_area["id"],
        "activities": [
            _fake_activity(
                faker_factory=faker_factory,
            )
            for _ in range(random.randint(0, 5))
        ],
    }


def fake_values_inventory_factory(
    *,
    faker_factory: faker.Faker,
    life_areas: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake value inventory documents.

    Although patients will be asked to populate these,
    ensure functionality even if they are not yet populated.
    """

    def factory() -> dict:
        fake_values_inventory = {
            "_type": "valuesInventory",
            "assigned": random.choice([True, False]),
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(faker_factory.date_time())
            ),
            "lastUpdatedDateTime": date_utils.format_datetime(
                pytz.utc.localize(faker_factory.date_time())
            ),
        }

        values = []
        for life_area_current in life_areas:
            for _ in range(random.randint(0, 5)):
                values.append(
                    _fake_value(
                        faker_factory=faker_factory,
                        life_area=life_area_current,
                    )
                )
        if values:
            fake_values_inventory["values"] = values

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
    data_fake_life_area_contents_factory: Callable[[], List[dict]],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_values_inventory_factory.
    """

    life_area_contents = data_fake_life_area_contents_factory()

    unvalidated_factory = fake_values_inventory_factory(
        faker_factory=faker,
        life_areas=life_area_contents,
    )

    def factory() -> dict:
        fake_values_inventory = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.values_inventory_schema,
            data=fake_values_inventory,
        )

        return fake_values_inventory

    return factory
