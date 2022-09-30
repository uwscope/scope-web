import datetime
import faker
import pytest
import pytz
import random
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activity_schedules
import scope.database.patient.scheduled_activities
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def _fake_scheduled_activity(
    *,
    faker_factory: faker.Faker,
    activity_schedule: dict,
) -> dict:
    return {
        "_type": scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
        scope.database.patient.activity_schedules.SEMANTIC_SET_ID: activity_schedule[
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
        ],
        "dueDate": date_utils.format_date(
            faker_factory.date_between(
                start_date=datetime.date.today() - datetime.timedelta(days=10),
                end_date=datetime.date.today() + datetime.timedelta(days=10),
            )
        ),
        "dueTimeOfDay": random.randint(0, 23),
        "dueDateTime": date_utils.format_datetime(
            pytz.utc.localize(
                faker_factory.date_time_between(
                    start_date=datetime.datetime.utcnow() - datetime.timedelta(days=10),
                    end_date=datetime.datetime.utcnow() + datetime.timedelta(days=10),
                )
            )
        ),
        #  hasReminder currently must be false
        #
        # "reminderDate": date_utils.format_date(
        #     faker_factory.date_between(
        #         start_date=datetime.date.today() - datetime.timedelta(days=10),
        #         end_date=datetime.date.today() + datetime.timedelta(days=10),
        #     )
        # ),
        # "reminderTimeOfDay": random.randint(0, 23),
        # "reminderDateTime": date_utils.format_datetime(
        #     pytz.utc.localize(
        #         faker_factory.date_time_between(
        #             start_date=datetime.datetime.utcnow() - datetime.timedelta(days=10),
        #             end_date=datetime.datetime.utcnow() + datetime.timedelta(days=10),
        #         )
        #     )
        # ),
        "completed": random.choice([True, False]),
    }


def _fake_scheduled_activities(
    *,
    faker_factory: faker.Faker,
    activity_schedules: List[dict],
) -> List[dict]:
    fake_scheduled_activities = []
    for fake_activity_schedule in activity_schedules:
        fake_scheduled_activities.append(
            _fake_scheduled_activity(
                faker_factory=faker_factory,
                activity_schedule=fake_activity_schedule,
            )
        )
    return fake_scheduled_activities


def fake_scheduled_activity_factory(
    *,
    faker_factory: faker.Faker,
    activities: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake scheduled activity document.
    """

    def factory() -> dict:
        fake_scheduled_activities = fake_scheduled_activities_factory(
            faker_factory=faker_factory,
            activities=activities,
        )()

        fake_scheduled_activity = random.choice(fake_scheduled_activities)

        return fake_scheduled_activity

    return factory


def fake_scheduled_activities_factory(
    *,
    faker_factory: faker.Faker,
    activity_schedules: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake scheduled activity documents.
    """

    if len(activity_schedules) < 1:
        raise ValueError("activity schedules must include at least one element.")

    for activity_schedule_current in activity_schedules:
        if (
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
            not in activity_schedule_current
        ):
            raise ValueError(
                'activity schedules must include "{}".'.format(
                    scope.database.patient.activity_schedules.SEMANTIC_SET_ID
                )
            )

    def factory() -> List[dict]:
        fake_scheduled_activities = _fake_scheduled_activities(
            faker_factory=faker_factory,
            activity_schedules=activity_schedules,
        )

        return fake_scheduled_activities

    return factory


@pytest.fixture(name="data_fake_scheduled_activity_factory")
def fixture_data_fake_scheduled_activity_factory(
    faker: faker.Faker,
    data_fake_scheduled_activities_factory: Callable[[], List[dict]],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_scheduled_activity_factory.
    """

    def factory() -> dict:
        fake_scheduled_activity = random.choice(
            data_fake_scheduled_activities_factory()
        )

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.scheduled_activity_schema,
            data=fake_scheduled_activity,
        )

        return fake_scheduled_activity

    return factory


@pytest.fixture(name="data_fake_scheduled_activities_factory")
def fixture_data_fake_scheduled_activities_factory(
    faker: faker.Faker,
    data_fake_activity_schedules_factory: Callable[[], List[dict]],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_scheduled_activity_factory.
    """

    # activities may randomly not include any elements.
    # Scheduled activities are not defined in such a scenario.
    # Generate new activity schedules that includes at least one element.
    activity_schedules = data_fake_activity_schedules_factory()
    while not len(activity_schedules) > 0:
        activity_schedules = data_fake_activity_schedules_factory()

    # Simulate IDs that can be referenced in fake scheduled activities
    for activity_schedule_current in activity_schedules:
        generated_set_id = collection_utils.generate_set_id()
        activity_schedule_current["_set_id"] = generated_set_id
        activity_schedule_current[
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
        ] = generated_set_id

    unvalidated_factory = fake_scheduled_activities_factory(
        faker_factory=faker,
        activity_schedules=activity_schedules,
    )

    def factory() -> List[dict]:
        fake_scheduled_activities = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.scheduled_activities_schema,
            data=fake_scheduled_activities,
        )

        return fake_scheduled_activities

    return factory
