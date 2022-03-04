import datetime
import faker
import pytest
import random
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.scheduled_activities
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def _fake_scheduled_activity(
    *,
    faker_factory: faker.Faker,
    activity: dict,
) -> dict:
    return {
        "_type": scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
        "dueDate": date_utils.format_date(
            faker_factory.date_between_dates(
                date_start=datetime.datetime.now() - datetime.timedelta(days=10),
                date_end=datetime.datetime.now() + datetime.timedelta(days=10),
            )
        ),
        "dueType": fake_utils.fake_enum_value(scope.enums.DueType),
        scope.database.patient.activities.SEMANTIC_SET_ID: activity[
            scope.database.patient.activities.SEMANTIC_SET_ID
        ],
        "activityName": activity["name"],
        "reminder": date_utils.format_date(
            faker_factory.date_between_dates(
                date_start=datetime.datetime.now(),
                date_end=datetime.datetime.now() + datetime.timedelta(days=7),
            )
        ),
        "completed": random.choice([True, False]),
    }


def _fake_scheduled_activities(
    *,
    faker_factory: faker.Faker,
    activities: List[dict],
) -> List[dict]:
    fake_scheduled_activities = []
    for fake_activity in activities:
        fake_scheduled_activities.append(
            _fake_scheduled_activity(
                faker_factory=faker_factory,
                activity=fake_activity,
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
    activities: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake scheduled activity documents.
    """

    if len(activities) < 1:
        raise ValueError("activities must include at least one element.")

    for activity_current in activities:
        if scope.database.patient.activities.SEMANTIC_SET_ID not in activity_current:
            raise ValueError(
                'activities must include "{}".'.format(
                    scope.database.patient.activities.SEMANTIC_SET_ID
                )
            )

    def factory() -> List[dict]:
        fake_scheduled_activities = _fake_scheduled_activities(
            faker_factory=faker_factory,
            activities=activities,
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
    data_fake_activities_factory: Callable[[], List[dict]],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_scheduled_activity_factory.
    """

    # activities may randomly not include any elements.
    # Scheduled activities are not defined in such a scenario.
    # Generate a new activities that includes at least one element.
    activities = data_fake_activities_factory()
    while not len(activities) > 0:
        activities = data_fake_activities_factory()

    # Simulate IDs that can be referenced in fake scheduled activities
    for activity_current in activities:
        generated_set_id = collection_utils.generate_set_id()
        activity_current["_set_id"] = generated_set_id
        activity_current[
            scope.database.patient.activities.SEMANTIC_SET_ID
        ] = generated_set_id

    unvalidated_factory = fake_scheduled_activities_factory(
        faker_factory=faker,
        activities=activities,
    )

    def factory() -> List[dict]:
        fake_scheduled_activities = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.scheduled_activities_schema,
            data=fake_scheduled_activities,
        )

        return fake_scheduled_activities

    return factory
