import datetime
import faker as _faker
import pytest
import pytz
import random
from typing import Callable

import scope.database.date_utils as date_utils
import scope.schema
import scope.schema_utils


def fake_values_inventory_factory(
    *,
    faker: _faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake value inventory documents.
    """

    def factory() -> dict:
        datetime_now = datetime.datetime.now()

        fake_values_inventory = {
            "_type": "valuesInventory",
            "assigned": random.choice([False, True]),
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime_now)
            ),
        }

        return fake_values_inventory

    return factory


@pytest.fixture(name="data_fake_values_inventory_factory")
def fixture_data_fake_values_inventory_factory(
    *,
    faker: _faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_values_inventory_factory.
    """

    unvalidated_factory = fake_values_inventory_factory(
        faker=faker,
    )

    def factory() -> dict:
        fake_values_inventory = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.values_inventory_schema,
            data=fake_values_inventory,
        )

        return fake_values_inventory

    return factory
