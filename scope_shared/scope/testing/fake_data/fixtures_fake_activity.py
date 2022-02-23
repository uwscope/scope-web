import datetime
import faker
import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.database.format_utils as format_utils
import scope.database.patient.activities

import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils
import scope.testing.schema


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
            "startDate": format_utils.format_date(
                faker_factory.date_between_dates(
                    date_start=datetime.datetime.now(),
                    date_end=datetime.datetime.now() + datetime.timedelta(days=60),
                )
            ),
            "timeOfDay": random.randrange(1, 25),
            "hasReminder": random.choice([True, False]),
            "reminderTimeOfDay": random.randrange(1, 25),
            "hasRepetition": random.choice([True, False]),
            "repeatDayFlags": fake_utils.fake_enum_flag_values(
                scope.testing.fake_data.enums.DayOfWeek
            ),
            "isActive": random.choice([True, False]),
            "isDeleted": random.choice([True, False]),
        }

        return document_utils.normalize_document(document=fake_activity)

    return factory


@pytest.fixture(name="data_fake_activity_factory")
def fixture_data_fake_activity_factory(
    faker: faker.Faker,
    data_fake_values_inventory_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_activity_factory.
    """

    # A values inventory may randomly not include any values.
    # Activites are not defined in such a scenario.
    # Generate a new values inventory that includes at least one value.
    values_inventory = data_fake_values_inventory_factory()
    while not len(values_inventory.get("values", [])) > 0:
        values_inventory = data_fake_values_inventory_factory()

    unvalidated_factory = fake_activity_factory(
        faker_factory=faker,
        values_inventory=values_inventory,
    )

    def factory() -> dict:
        fake_activity = unvalidated_factory()

        scope.testing.schema.assert_schema(
            data=fake_activity,
            schema=scope.schema.activity_schema,
            expected_valid=True,
        )

        fake_utils.xfail_for_invalid(
            schema=scope.schema.activity_schema,
            document=fake_activity,
        )

        return fake_activity

    return factory
