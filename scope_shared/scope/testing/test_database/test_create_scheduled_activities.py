import datetime
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.scheduled_activities
import scope.schema
import scope.schema_utils as schema_utils


def _dummy_inserted_activity(
    fake_activity_factory: Callable[[], dict],
    has_repetition: bool,
    has_reminder: bool = False,
) -> dict:
    activity = fake_activity_factory()
    # Assume activity has just been inserted into db using POST
    # create_scheduled_activities method needs activity to have its SEMANTIC_SET_ID
    activity[
        scope.database.patient.activities.SEMANTIC_SET_ID
    ] = collection_utils.generate_set_id()
    activity["hasRepetition"] = has_repetition
    activity["hasReminder"] = has_reminder
    return activity


def _scheduled_activities_assertions(
    activity: dict,
    scheduled_activities: List[dict],
) -> None:
    schema_utils.assert_schema(
        data=scheduled_activities,
        schema=scope.schema.scheduled_activities_schema,
    )
    for scheduled_activity_current in scheduled_activities:
        assert not scheduled_activity_current["completed"]
        assert scheduled_activity_current["dueType"] == "Exact"

    if not activity["hasRepetition"]:
        assert len(scheduled_activities) == 1
        assert scheduled_activities[0]["dueDate"] == date_utils.format_datetime(
            datetime.datetime.combine(
                date_utils.parse_date(activity["startDate"]),
                datetime.time(hour=activity["timeOfDay"]),
            )
        )
        if not activity["hasReminder"]:
            assert scheduled_activities[0]["reminder"] == None
        else:
            assert scheduled_activities[0]["reminder"] == date_utils.format_datetime(
                datetime.datetime.combine(
                    date_utils.parse_date(activity["startDate"]),
                    datetime.time(hour=activity["reminderTimeOfDay"]),
                )
            )


# TODO: Check if "test" function names could be better.
def test_create_scheduled_activities_condition_one(
    data_fake_activity_factory: Callable[[], dict],
):
    # Condition 1 - hasRepetition is False
    activity = _dummy_inserted_activity(
        fake_activity_factory=data_fake_activity_factory,
        has_repetition=False,
    )

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity
        )
    )

    _scheduled_activities_assertions(
        activity=activity,
        scheduled_activities=scheduled_activities,
    )


def test_create_scheduled_activities_condition_one_subcondition_one(
    data_fake_activity_factory: Callable[[], dict],
):
    # Condition 1 - hasRepetition is False, Subcondition 1 - hasReminder is False
    activity = _dummy_inserted_activity(
        fake_activity_factory=data_fake_activity_factory,
        has_repetition=False,
        has_reminder=False,
    )

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity
        )
    )

    _scheduled_activities_assertions(
        activity=activity,
        scheduled_activities=scheduled_activities,
    )


def test_create_scheduled_activities_condition_one_subcondition_two(
    data_fake_activity_factory: Callable[[], dict],
):
    # Condition 1 - hasRepetition is False, Subcondition 2 - hasReminder is True

    activity = _dummy_inserted_activity(
        fake_activity_factory=data_fake_activity_factory,
        has_repetition=False,
        has_reminder=True,
    )

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity
        )
    )

    _scheduled_activities_assertions(
        activity=activity,
        scheduled_activities=scheduled_activities,
    )

    # TODO: hasRepetition is True left.
