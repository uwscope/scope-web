import datetime
import faker
import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.database.format_utils as format_utils
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


# TODO: Get the generation verified.

# TODO: James Comment 2/22:  I am not sure this is all correct / consistent

# TODO: This will create invalid activities if fake_values_inventory["values"] == []


def fake_activity_factory(
    *,
    faker_factory: faker.Faker,
    fake_life_areas: List[dict],  # lifeareaId will be taken from this
    fake_values_inventory: dict,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake activity documents.
    """

    def factory() -> dict:
        names = []
        for value in fake_values_inventory["values"]:
            for activity in value["activities"]:
                names.append(activity["name"])

        name = random.choice(
            [
                faker_factory.text(),
                random.choice(names),
            ]
        )

        fake_activity = {
            "_type": "activity",
            "name": name,
            "value": random.choice(
                [
                    value["name"] for value in fake_values_inventory["values"]
                ]  # TODO: This will be empty if "values" is an empty list
            ),
            "lifeareaId": random.choice(
                [fake_life_area["id"] for fake_life_area in fake_life_areas]
            ),
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
    data_fake_life_areas: List[dict],
    data_fake_values_inventory: dict,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_activity_factory.
    """

    unvalidated_factory = fake_activity_factory(
        faker_factory=faker,
        fake_life_areas=data_fake_life_areas,
        fake_values_inventory=data_fake_values_inventory,
    )

    def factory() -> dict:
        fake_activity = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.activity_schema,
            document=fake_activity,
        )

        return fake_activity

    return factory
