import datetime
import faker
import pytest
import pytz
import random
from typing import Callable

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.enums
import scope.schema
import scope.schema_utils
import scope.schema_utils as schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


# Keys are not naively optional, see allowable_schedules
OPTIONAL_KEYS = []


def _fake_activity(
    *,
    faker_factory: faker.Faker,
    values_inventory: dict,
) -> dict:

    combined_activities = []
    for value_current in values_inventory["values"]:
        combined_activities.extend(value_current.get("activities", []))

    if len(combined_activities) > 0 and random.choice([True, False]):
        # Sample a value with at least one activity
        values_valid = []
        for value_current in values_inventory["values"]:
            if value_current.get("activities", []):
                values_valid.append(value_current)
        activity_value = random.choice(values_valid)

        # Sample an activity
        activity_name = random.choice(activity_value["activities"])["name"]
    else:
        # Sample any value
        activity_value = random.choice(values_inventory["values"])

        # Generate a text-based activity
        activity_name = faker_factory.text()

    fake_activity = {
        "_type": scope.database.patient.activities.DOCUMENT_TYPE,
        "name": activity_name,
        "value": activity_value["name"],
        "lifeareaId": activity_value["lifeareaId"],
        "startDateTime": date_utils.format_datetime(
            pytz.utc.localize(
                faker_factory.date_time_between(
                    start_date=datetime.datetime.now()
                    - datetime.timedelta(days=1 * 30),
                    end_date=datetime.datetime.now() + datetime.timedelta(days=1 * 30),
                )
            )
        ),
        "timeOfDay": random.randrange(0, 24),
    }
    allowable_schedules = [
        {
            "hasReminder": True,
            "reminderTimeOfDay": random.randrange(0, 24),
            "hasRepetition": False,
            "isActive": True,
            "isDeleted": False,
        },
        {
            "hasReminder": True,
            "reminderTimeOfDay": random.randrange(0, 24),
            "hasRepetition": False,
            "isActive": False,
            "isDeleted": True,
        },
        {
            "hasReminder": True,
            "reminderTimeOfDay": random.randrange(0, 24),
            "hasRepetition": True,
            "repeatDayFlags": fake_utils.fake_enum_flag_values(scope.enums.DayOfWeek),
            "isActive": True,
            "isDeleted": False,
        },
        {
            "hasReminder": True,
            "reminderTimeOfDay": random.randrange(0, 24),
            "hasRepetition": True,
            "repeatDayFlags": fake_utils.fake_enum_flag_values(scope.enums.DayOfWeek),
            "isActive": False,
            "isDeleted": True,
        },
        {
            "hasReminder": False,
            "hasRepetition": False,
            "isActive": True,
            "isDeleted": False,
        },
        {
            "hasReminder": False,
            "hasRepetition": False,
            "isActive": False,
            "isDeleted": True,
        },
        {
            "hasReminder": False,
            "hasRepetition": True,
            "repeatDayFlags": fake_utils.fake_enum_flag_values(scope.enums.DayOfWeek),
            "isActive": True,
            "isDeleted": False,
        },
        {
            "hasReminder": False,
            "hasRepetition": True,
            "repeatDayFlags": fake_utils.fake_enum_flag_values(scope.enums.DayOfWeek),
            "isActive": False,
            "isDeleted": True,
        },
    ]

    fake_activity.update(random.choice(allowable_schedules))

    # Remove a randomly sampled subset of optional parameters.
    fake_activity = fake_utils.fake_optional(
        document=fake_activity,
        optional_keys=OPTIONAL_KEYS,
    )

    return fake_activity


def fake_activity_factory(
    *,
    faker_factory: faker.Faker,
    values_inventory: dict,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake activity documents.
    """

    if not len(values_inventory.get("values", [])) > 0:
        raise ValueError("values_inventory must include at least one value.")

    def factory() -> dict:
        fake_activity = _fake_activity(
            faker_factory=faker_factory,
            values_inventory=values_inventory,
        )

        return fake_activity

    return factory


@pytest.fixture(name="data_fake_activity_factory")
def fixture_data_fake_activity_factory(
    faker: faker.Faker,
    data_fake_values_inventory_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_activity_factory.
    """

    def factory() -> dict:
        # A values inventory may randomly not include any values.
        # Activities are not defined in such a scenario.
        # Generate a new values inventory that includes at least one value.
        values_inventory = data_fake_values_inventory_factory()
        while not len(values_inventory.get("values", [])) > 0:
            values_inventory = data_fake_values_inventory_factory()

        unvalidated_factory = fake_activity_factory(
            faker_factory=faker,
            values_inventory=values_inventory,
        )

        fake_activity = unvalidated_factory()

        schema_utils.assert_schema(
            data=fake_activity,
            schema=scope.schema.activity_schema,
        )

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.activity_schema,
            data=fake_activity,
        )

        return fake_activity

    return factory
