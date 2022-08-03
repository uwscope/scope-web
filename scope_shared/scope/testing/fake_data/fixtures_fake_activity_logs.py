import faker
import pytest
import random
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.scheduled_activities
import scope.enums
import scope.schema
import scope.schema_utils
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
    scheduled_activities: List[dict],
) -> List[dict]:
    if len(scheduled_activities) > 1:
        sampled_scheduled_activities = random.sample(
            scheduled_activities, random.randint(1, len(scheduled_activities))
        )
    else:
        sampled_scheduled_activities = scheduled_activities

    fake_activity_logs = []
    for fake_scheduled_activity in sampled_scheduled_activities:
        fake_activity_log = {
            "_type": scope.database.patient.activity_logs.DOCUMENT_TYPE,
            scope.database.patient.scheduled_activities.SEMANTIC_SET_ID: fake_scheduled_activity[
                scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
            ],
            scope.database.patient.activities.SEMANTIC_SET_ID: fake_scheduled_activity[
                scope.database.patient.activities.SEMANTIC_SET_ID
            ],
            "activityName": fake_scheduled_activity["activityName"],
            "recordedDateTime": fake_scheduled_activity["dueDateTime"],
            "comment": faker_factory.text(),
            "completed": random.choice([True, False]),
            "success": fake_utils.fake_enum_value(scope.enums.ActivitySuccessType),
            "alternative": faker_factory.text(),
        }
        if fake_activity_log["success"] != scope.enums.ActivitySuccessType.No.value:
            fake_activity_log.update(
                {
                    "pleasure": random.randint(1, 10),
                    "accomplishment": random.randint(1, 10),
                }
            )
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
    scheduled_activities: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake activity log document.
    """

    def factory() -> dict:
        fake_activity_logs = fake_activity_logs_factory(
            faker_factory=faker_factory,
            scheduled_activities=scheduled_activities,
        )()

        fake_activity_log = random.choice(fake_activity_logs)

        return fake_activity_log

    return factory


def fake_activity_logs_factory(
    *,
    faker_factory: faker.Faker,
    scheduled_activities: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake activity log documents.
    """

    if len(scheduled_activities) < 1:
        raise ValueError("scheduled_activities must include at least one element.")

    for scheduled_activity_current in scheduled_activities:
        if (
            scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
            not in scheduled_activity_current
        ):
            raise ValueError(
                'scheduled_activities must include "{}".'.format(
                    scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
                )
            )

    def factory() -> List[dict]:
        fake_activity_logs = _fake_activity_logs(
            faker_factory=faker_factory,
            scheduled_activities=scheduled_activities,
        )

        return fake_activity_logs

    return factory


@pytest.fixture(name="data_fake_activity_log_factory")
def fixture_data_fake_activity_log_factory(
    faker: faker.Faker,
    data_fake_activity_logs_factory: Callable[[], List[dict]],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_activity_log_factory.
    """

    def factory() -> dict:
        fake_activity_log = random.choice(data_fake_activity_logs_factory())

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.activity_log_schema,
            data=fake_activity_log,
        )

        return fake_activity_log

    return factory


@pytest.fixture(name="data_fake_activity_logs_factory")
def fixture_data_fake_activity_logs_factory(
    faker: faker.Faker,
    data_fake_scheduled_activities_factory: Callable[[], List[dict]],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_activity_logs_factory.
    """

    scheduled_activities = data_fake_scheduled_activities_factory()

    # Simulate IDs that can be referenced in fake activity logs
    for scheduled_activity_current in scheduled_activities:
        generated_set_id = collection_utils.generate_set_id()
        scheduled_activity_current["_set_id"] = generated_set_id
        scheduled_activity_current[
            scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
        ] = generated_set_id

    unvalidated_factory = fake_activity_logs_factory(
        faker_factory=faker,
        scheduled_activities=scheduled_activities,
    )

    def factory() -> List[dict]:
        fake_activity_logs = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.activity_logs_schema,
            data=fake_activity_logs,
        )

        return fake_activity_logs

    return factory
