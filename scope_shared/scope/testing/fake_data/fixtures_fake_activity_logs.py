import datetime
import faker
import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.database.format_utils as format_utils
import scope.database.patient.activity_logs
import scope.database.patient.scheduled_activities
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS = [
    "completed",
    "success",
    "alternative",
    "pleasure",
    "accomplishment",
]


def _fake_activity_logs(
    *,
    faker_factory: faker.Faker,
    fake_scheduled_activities: List[dict],
) -> List[dict]:

    # TODO: Discuss w/ James.
    if fake_scheduled_activities == []:
        return []

    n = random.randint(1, len(fake_scheduled_activities))

    fake_activity_logs = []
    for fake_scheduled_activity in random.sample(fake_scheduled_activities, n):
        # TODO: Discuss w/ James.
        if fake_scheduled_activity == {}:
            continue
        fake_activity_log = {
            "_type": scope.database.patient.activity_logs.DOCUMENT_TYPE,
            "recordedDate": fake_scheduled_activity["dueDate"],
            "comment": faker_factory.text(),
            "scheduleId": fake_scheduled_activity[
                scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
            ],
            "activityName": fake_scheduled_activity["activityName"],
            "completed": random.choice([True, False]),
            "success": fake_utils.fake_enum_value(
                scope.testing.fake_data.enums.ActivitySuccessType
            ),
            "alternative": faker_factory.text(),
            "pleasure": random.randint(1, 10),
            "accomplishment": random.randint(1, 10),
        }
        # Remove a randomly sampled subset of optional parameters.
        fake_activity_log = fake_utils.fake_optional(
            document=fake_activity_log,
            optional_keys=OPTIONAL_KEYS,
        )
        fake_activity_logs.append(fake_activity_log)

    return fake_activity_logs


def fake_activity_log_factory(
    *,
    faker_factory: faker.Faker,
    fake_scheduled_activities: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake activity log document.
    """

    def factory() -> dict:

        # TODO: Needs to be fixed/removed after resolving values inventory issue
        if fake_scheduled_activities == []:
            return {}

        fake_activity_log = random.choice(
            _fake_activity_logs(
                faker_factory=faker_factory,
                fake_scheduled_activities=fake_scheduled_activities,
            )
        )

        return document_utils.normalize_document(document=fake_activity_log)

    return factory


def fake_activity_logs_factory(
    *,
    faker_factory: faker.Faker,
    fake_scheduled_activities: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake activity log documents.
    """

    def factory() -> dict:

        fake_activity_logs = _fake_activity_logs(
            faker_factory=faker_factory,
            fake_scheduled_activities=fake_scheduled_activities,
        )

        return document_utils.normalize_documents(documents=fake_activity_logs)

    return factory


@pytest.fixture(name="data_fake_activity_log_factory")
def fixture_data_fake_activity_log_factory(
    faker: faker.Faker,
    data_fake_scheduled_activities: List[dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_activity_log_factory.
    """

    unvalidated_factory = fake_activity_log_factory(
        faker_factory=faker,
        fake_scheduled_activities=data_fake_scheduled_activities,
    )

    def factory() -> dict:
        fake_activity_log = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.activity_log_schema,
            document=fake_activity_log,
        )

        return fake_activity_log

    return factory


@pytest.fixture(name="data_fake_activity_logs_factory")
def fixture_data_fake_activity_logs_factory(
    faker: faker.Faker,
    data_fake_scheduled_activities: List[dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_activity_logs_factory.
    """

    unvalidated_factory = fake_activity_logs_factory(
        faker_factory=faker,
        fake_scheduled_activities=data_fake_scheduled_activities,
    )

    def factory() -> dict:
        fake_activity_logs = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.activity_logs_schema,
            document=fake_activity_logs,
        )

        return fake_activity_logs

    return factory
