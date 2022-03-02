import datetime
from typing import Callable, List

import pytest
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

        if not activity[
            "hasReminder"
        ]:  # CONDITION 1 - hasRepetition is False, Subcondition 1 - hasReminder is False
            assert scheduled_activities[0]["reminder"] == None
        else:  # CONDITION 1 - hasRepetition is False, Subcondition 2 - hasReminder is True
            assert scheduled_activities[0]["reminder"] == date_utils.format_datetime(
                datetime.datetime.combine(
                    date_utils.parse_date(activity["startDate"]),
                    datetime.time(hour=activity["reminderTimeOfDay"]),
                )
            )
    else:
        for scheduled_activity_current in scheduled_activities:
            if not activity[
                "hasReminder"
            ]:  # CONDITION 2 - hasRepetition is True, Subcondition 1 - hasReminder is False
                assert scheduled_activity_current["reminder"] == None
            else:  # CONDITION 2 - hasRepetition is True, Subcondition 2 - hasReminder is True
                scheduled_activity_day_date = date_utils.format_date(
                    date_utils.parse_datetime(scheduled_activity_current["dueDate"]),
                )
                assert scheduled_activity_current[
                    "reminder"
                ] == date_utils.format_datetime(
                    datetime.datetime.combine(
                        date_utils.parse_date(scheduled_activity_day_date),
                        datetime.time(hour=activity["reminderTimeOfDay"]),
                    )
                )


def test_create_scheduled_activities_condition_one_subcondition_one(
    data_fake_activity_factory: Callable[[], dict],
):
    # CONDITION 1 - hasRepetition is False, Subcondition 1 - hasReminder is False
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
    # CONDITION 1 - hasRepetition is False, Subcondition 2 - hasReminder is True
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


@pytest.mark.parametrize(
    "start_date,time_of_day,repeat_day_flags,weeks,scheduled_activity_due_dates",
    [
        (
            "2022-03-01T00:00:00Z",  # Monday
            16,
            {
                "Monday": True,
                "Tuesday": True,
                "Wednesday": False,
                "Thursday": True,
                "Friday": False,
                "Saturday": False,
                "Sunday": False,
            },
            1,
            [
                "2022-03-01T16:00:00Z",
                "2022-03-03T16:00:00Z",
                "2022-03-07T16:00:00Z",
                "2022-03-08T16:00:00Z",
            ],
        ),
        (
            "2022-04-01T00:00:00Z",  # Friday
            7,
            {
                "Monday": True,
                "Tuesday": True,
                "Wednesday": False,
                "Thursday": True,
                "Friday": False,
                "Saturday": False,
                "Sunday": False,
            },
            2,
            [
                "2022-04-04T07:00:00Z",
                "2022-04-05T07:00:00Z",
                "2022-04-07T07:00:00Z",
                "2022-04-11T07:00:00Z",
                "2022-04-12T07:00:00Z",
                "2022-04-14T07:00:00Z",
            ],
        ),
    ],
)
def test_create_scheduled_activities_condition_two(
    data_fake_activity_factory: Callable[[], dict],
    start_date: str,
    time_of_day: int,
    repeat_day_flags: dict,
    weeks: int,
    scheduled_activity_due_dates: List[str],
):
    # CONDITION 2 - hasRepetition is True, Subcondition 1 - hasReminder is False
    activity = _dummy_inserted_activity(
        fake_activity_factory=data_fake_activity_factory,
        has_repetition=True,
        has_reminder=False,
    )

    activity["startDate"] = start_date
    activity["timeOfDay"] = time_of_day
    activity["repeatDayFlags"] = repeat_day_flags

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity,
            weeks=weeks,
        )
    )

    assert (
        [
            scheduled_activity_current["dueDate"]
            for scheduled_activity_current in scheduled_activities
        ]
    ) == scheduled_activity_due_dates

    _scheduled_activities_assertions(
        activity=activity,
        scheduled_activities=scheduled_activities,
    )

    # CONDITION 2 - hasRepetition is True, Subcondition 2 - hasReminder is True
    activity = _dummy_inserted_activity(
        fake_activity_factory=data_fake_activity_factory,
        has_repetition=True,
        has_reminder=True,
    )

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity,
            weeks=weeks,
        )
    )

    assert (
        [
            scheduled_activity_current["dueDate"]
            for scheduled_activity_current in scheduled_activities
        ]
    ) == scheduled_activity_due_dates

    _scheduled_activities_assertions(
        activity=activity,
        scheduled_activities=scheduled_activities,
    )
