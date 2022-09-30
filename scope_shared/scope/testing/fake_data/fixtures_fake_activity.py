import datetime
import faker as _faker
import pytest
import pytz
import random
from typing import Callable

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


# Keys are not naively optional, see allowable_schedules
OPTIONAL_KEYS = []


def _fake_activity(
    *,
    faker: _faker.Faker,
) -> dict:
    datetime_now = datetime.datetime.now()

    fake_activity = {
        "_type": scope.database.patient.activities.DOCUMENT_TYPE,
        "name": faker.text(),
        "editedDateTime": date_utils.format_datetime(
            pytz.utc.localize(
                datetime_now,
            )
        ),
        "enjoyment": random.randint(0, 10),
        "importance": random.randint(0, 10),
        "isActive": random.choice([False, True]),
        "isDeleted": random.choice([False, True]),
    }

    # Remove a randomly sampled subset of independently optional parameters
    fake_activity = fake_utils.fake_optional(
        document=fake_activity,
        optional_keys=[
            "enjoyment",
            "importance",
        ],
    )

    # Apply fields with complex relationships
    value_choices = [
        {},
        {
            "valueId": "valueId Placeholder",
        },
    ]
    fake_activity.update(random.choice(value_choices))

    return fake_activity


def fake_activity_factory(
    *,
    faker: _faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake activity documents.
    """

    def factory() -> dict:
        fake_activity = _fake_activity(
            faker=faker,
        )

        return fake_activity

    return factory


@pytest.fixture(name="data_fake_activity_factory")
def fixture_data_fake_activity_factory(
    faker: _faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_activity_factory.
    """

    def factory() -> dict:
        unvalidated_factory = fake_activity_factory(faker=faker)

        fake_activity = unvalidated_factory()

        schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.activity_schema,
            data=fake_activity,
        )

        return fake_activity

    return factory
