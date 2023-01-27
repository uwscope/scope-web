import datetime
import faker
import pytest
import pytz
import random
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.activity_schedules
import scope.database.patient.scheduled_activities
import scope.database.patient.values
import scope.enums
import scope.schema
import scope.schema_utils


def _fake_scheduled_activity(
    *,
    faker_factory: faker.Faker,
    data_snapshot: dict,
) -> dict:
    return {
        "_type": scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
        scope.database.patient.activity_schedules.SEMANTIC_SET_ID: data_snapshot[
            scope.database.patient.activity_schedules.DOCUMENT_TYPE
        ][scope.database.patient.activity_schedules.SEMANTIC_SET_ID],
        "dataSnapshot": data_snapshot,
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
    data_snapshots: List[dict],
) -> List[dict]:
    fake_scheduled_activities = []
    for fake_data_snapshot in data_snapshots:
        fake_scheduled_activities.append(
            _fake_scheduled_activity(
                faker_factory=faker_factory,
                data_snapshot=fake_data_snapshot,
            )
        )
    return fake_scheduled_activities


def fake_scheduled_activities_factory(
    *,
    faker_factory: faker.Faker,
    data_snapshots: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake scheduled activity documents.
    """

    if len(data_snapshots) < 1:
        raise ValueError("data snapshots must include at least one element.")

    for data_snapshot in data_snapshots:
        if (
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
            not in data_snapshot[
                scope.database.patient.activity_schedules.DOCUMENT_TYPE
            ]
        ):
            raise ValueError(
                'activity schedule in data snapshot must include "{}".'.format(
                    scope.database.patient.activity_schedules.SEMANTIC_SET_ID
                )
            )

        if (
            scope.database.patient.activities.SEMANTIC_SET_ID
            not in data_snapshot[scope.database.patient.activities.DOCUMENT_TYPE]
        ):
            raise ValueError(
                'activity in data snapshot must include "{}".'.format(
                    scope.database.patient.activities.SEMANTIC_SET_ID
                )
            )

        if (
            scope.database.patient.values.SEMANTIC_SET_ID
            in data_snapshot[scope.database.patient.activities.DOCUMENT_TYPE]
        ):
            if (
                scope.database.patient.values.SEMANTIC_SET_ID
                not in data_snapshot[scope.database.patient.values.DOCUMENT_TYPE]
            ):
                raise ValueError(
                    'value in data snapshot must include "{}" if activity has value.'.format(
                        scope.database.patient.values.SEMANTIC_SET_ID
                    )
                )

    def factory() -> List[dict]:
        fake_scheduled_activities = _fake_scheduled_activities(
            faker_factory=faker_factory,
            data_snapshots=data_snapshots,
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
    data_fake_activity_factory: Callable[[], dict],
    data_fake_value_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_scheduled_activities_factory.
    """

    data_snapshots = []
    activity_schedules = data_fake_activity_schedules_factory()

    # Create data snapshots and simulate IDs that can be referenced in fake scheduled activities
    for activity_schedule in activity_schedules:
        data_snapshot = {}

        # Create activity schedule
        generated_set_id = collection_utils.generate_set_id()
        activity_schedule["_set_id"] = generated_set_id
        activity_schedule[
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
        ] = generated_set_id
        data_snapshot[
            scope.database.patient.activity_schedules.DOCUMENT_TYPE
        ] = activity_schedule

        # Create activity
        activity = data_fake_activity_factory()
        activity["_set_id"] = activity_schedule[
            scope.database.patient.activities.SEMANTIC_SET_ID
        ]
        activity[scope.database.patient.activities.SEMANTIC_SET_ID] = activity_schedule[
            scope.database.patient.activities.SEMANTIC_SET_ID
        ]
        data_snapshot[scope.database.patient.activities.DOCUMENT_TYPE] = activity

        # Create value if activity has valueId
        if scope.database.patient.values.SEMANTIC_SET_ID in activity:
            value = data_fake_value_factory()
            value["_set_id"] = activity[scope.database.patient.values.SEMANTIC_SET_ID]
            value[scope.database.patient.values.SEMANTIC_SET_ID] = activity[
                scope.database.patient.values.SEMANTIC_SET_ID
            ]
            data_snapshot[scope.database.patient.values.DOCUMENT_TYPE] = value

        data_snapshots.append(data_snapshot)

    unvalidated_factory = fake_scheduled_activities_factory(
        faker_factory=faker,
        data_snapshots=data_snapshots,
    )

    def factory() -> List[dict]:
        fake_scheduled_activities = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.scheduled_activities_schema,
            data=fake_scheduled_activities,
        )

        return fake_scheduled_activities

    return factory
