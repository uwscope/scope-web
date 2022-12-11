import datetime
import faker as _faker
import pytest
import pytz
import random
from typing import Callable

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activity_schedules
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


# Keys are not naively optional, see allowable_schedules
OPTIONAL_KEYS = []


def _fake_activity_schedule(
    *,
    faker: _faker.Faker,
) -> dict:
    datetime_now = datetime.datetime.now()

    fake_activity_schedule = {
        "_type": scope.database.patient.activity_schedules.DOCUMENT_TYPE,
        "activityId": "activityId placeholder",
        "editedDateTime": date_utils.format_datetime(
            pytz.utc.localize(
                datetime_now,
            )
        ),
        "date": date_utils.format_date(
            pytz.utc.localize(
                faker.date_time_between(
                    start_date=datetime_now - datetime.timedelta(days=1 * 30),
                    end_date=datetime_now + datetime.timedelta(days=1 * 30),
                )
            )
        ),
        "timeOfDay": random.randrange(0, 24),
    }

    reminder_choices = [
        {
            "hasReminder": False,
        },
        #  hasReminder currently must be False
        #
        # {
        #     "hasReminder": True,
        #     "reminderTimeOfDay": random.randint(0, 23),
        # },
    ]
    fake_activity_schedule.update(random.choice(reminder_choices))

    repetition_choices = [
        {
            "hasRepetition": False,
        },
        {
            "hasRepetition": True,
            "repeatDayFlags": fake_utils.fake_enum_flag_values(scope.enums.DayOfWeek),
        },
    ]
    fake_activity_schedule.update(random.choice(repetition_choices))

    return fake_activity_schedule


def fake_activity_schedule_factory(
    *,
    faker: _faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake activity schedule documents.
    """

    def factory() -> dict:
        fake_activity_schedule = _fake_activity_schedule(
            faker=faker,
        )

        return fake_activity_schedule

    return factory


@pytest.fixture(name="data_fake_activity_schedule_factory")
def fixture_data_fake_activity_schedule_factory(
    faker: _faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_activity_schedule_factory.
    """

    def factory() -> dict:
        unvalidated_factory = fake_activity_schedule_factory(faker=faker)

        fake_activity_schedule = unvalidated_factory()

        schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.activity_schedule_schema,
            data=fake_activity_schedule,
        )

        return fake_activity_schedule

    return factory
