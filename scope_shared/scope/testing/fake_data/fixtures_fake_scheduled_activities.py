import datetime
import faker
import pytest
import random
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.document_utils as document_utils
import scope.database.format_utils as format_utils
import scope.database.patient.scheduled_activities
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def _fake_scheduled_activity(
    *,
    faker_factory: faker.Faker,
    fake_activity: dict,
) -> dict:
    return {
        # TODO: SET semantic set id because activity log needs it
        scope.database.patient.scheduled_activities.SEMANTIC_SET_ID: collection_utils.generate_set_id(),
        "_type": scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
        "dueDate": format_utils.format_date(
            faker_factory.date_between_dates(
                date_start=datetime.datetime.now() - datetime.timedelta(days=10),
                date_end=datetime.datetime.now() + datetime.timedelta(days=10),
            )
        ),
        "dueType": fake_utils.fake_enum_value(scope.testing.fake_data.enums.DueType),
        "activityId": fake_activity["activityId"],
        "activityName": fake_activity["name"],
        "reminder": format_utils.format_date(
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
    fake_activities: List[dict],
) -> List[dict]:
    fake_scheduled_activities = []
    for fake_activity in fake_activities:
        # TODO: fake_activity will be {} if "values" is None or [] in fake values inventory
        if fake_activity != {}:
            fake_scheduled_activities.append(
                _fake_scheduled_activity(
                    faker_factory=faker_factory,
                    fake_activity=fake_activity,
                )
            )
    return fake_scheduled_activities


def fake_scheduled_activity_factory(
    *,
    faker_factory: faker.Faker,
    fake_activities: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake scheduled activity document.
    """

    def factory() -> dict:

        fake_scheduled_activities = _fake_scheduled_activities(
            faker_factory=faker_factory,
            fake_activities=fake_activities,
        )

        if fake_scheduled_activities != []:
            fake_scheduled_activity = random.choice(fake_scheduled_activities)

            return document_utils.normalize_document(document=fake_scheduled_activity)
        else:
            return {}

    return factory


def fake_scheduled_activities_factory(
    *,
    faker_factory: faker.Faker,
    fake_activities: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake scheduled activity documents.
    """

    def factory() -> dict:

        fake_scheduled_activities = _fake_scheduled_activities(
            faker_factory=faker_factory,
            fake_activities=fake_activities,
        )

        return document_utils.normalize_documents(documents=fake_scheduled_activities)

    return factory


@pytest.fixture(name="data_fake_scheduled_activity_factory")
def fixture_data_fake_scheduled_activity_factory(
    faker: faker.Faker,
    data_fake_activities: List[dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_scheduled_activity_factory.
    """

    unvalidated_factory = fake_scheduled_activity_factory(
        faker_factory=faker,
        fake_activities=data_fake_activities,
    )

    def factory() -> dict:
        fake_scheduled_activity = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.scheduled_activity_schema,
            document=fake_scheduled_activity,
        )

        return fake_scheduled_activity

    return factory


@pytest.fixture(name="data_fake_scheduled_activities_factory")
def fixture_data_fake_scheduled_activities_factory(
    faker: faker.Faker,
    data_fake_activities: List[dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_scheduled_activity_factory.
    """

    unvalidated_factory = fake_scheduled_activities_factory(
        faker_factory=faker,
        fake_activities=data_fake_activities,
    )

    def factory() -> dict:
        fake_scheduled_activities = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.scheduled_activities_schema,
            document=fake_scheduled_activities,
        )

        return fake_scheduled_activities

    return factory


@pytest.fixture(name="data_fake_scheduled_activities")
def fixture_data_fake_activities(
    *,
    data_fake_scheduled_activities_factory: Callable[[], List[dict]],
) -> dict:
    """
    Fixture for data_fake_scheduled_activities.
    """

    return data_fake_scheduled_activities_factory()
