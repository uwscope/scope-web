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
        assert scheduled_activity_current["timeOfDay"] == activity["timeOfDay"]

    if not activity["hasRepetition"]:
        assert len(scheduled_activities) == 1
        assert scheduled_activities[0]["dueDate"] == activity["startDate"]

        if not activity[
            "hasReminder"
        ]:  # CONDITION 1 - hasRepetition is False, Subcondition 1 - hasReminder is False
            assert "reminderTimeOfDay" not in scheduled_activities[0]
        else:  # CONDITION 1 - hasRepetition is False, Subcondition 2 - hasReminder is True
            assert (
                scheduled_activities[0]["reminderTimeOfDay"]
                == activity["reminderTimeOfDay"]
            )
    else:
        for scheduled_activity_current in scheduled_activities:
            if not activity[
                "hasReminder"
            ]:  # CONDITION 2 - hasRepetition is True, Subcondition 1 - hasReminder is False
                assert "reminderTimeOfDay" not in scheduled_activity_current
            else:  # CONDITION 2 - hasRepetition is True, Subcondition 2 - hasReminder is True
                assert "reminderTimeOfDay" in scheduled_activity_current
                assert (
                    scheduled_activity_current["reminderTimeOfDay"]
                    == activity["reminderTimeOfDay"]
                )


@pytest.mark.parametrize(
    "activity_method",
    [("post"), ("put")],
)
def test_create_scheduled_activities_condition_one_subcondition_one(
    data_fake_activity_factory: Callable[[], dict],
    activity_method: str,
):
    # CONDITION 1 - hasRepetition is False, Subcondition 1 - hasReminder is False
    activity = _dummy_inserted_activity(
        fake_activity_factory=data_fake_activity_factory,
        has_repetition=False,
        has_reminder=False,
    )

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity,
            activity_method=activity_method,
        )
    )

    _scheduled_activities_assertions(
        activity=activity,
        scheduled_activities=scheduled_activities,
    )


@pytest.mark.parametrize(
    "activity_method",
    [("post"), ("put")],
)
def test_create_scheduled_activities_condition_one_subcondition_two(
    data_fake_activity_factory: Callable[[], dict],
    activity_method: str,
):
    # CONDITION 1 - hasRepetition is False, Subcondition 2 - hasReminder is True
    activity = _dummy_inserted_activity(
        fake_activity_factory=data_fake_activity_factory,
        has_repetition=False,
        has_reminder=True,
    )

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity,
            activity_method=activity_method,
        )
    )

    _scheduled_activities_assertions(
        activity=activity,
        scheduled_activities=scheduled_activities,
    )


@pytest.mark.parametrize(
    "start_date,time_of_day,repeat_day_flags,weeks,scheduled_activity_due_dates,activity_method",
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
                "2022-03-01T00:00:00Z",
                "2022-03-03T00:00:00Z",
                "2022-03-07T00:00:00Z",
                "2022-03-08T00:00:00Z",
            ],
            "post",
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
                "2022-04-04T00:00:00Z",
                "2022-04-05T00:00:00Z",
                "2022-04-07T00:00:00Z",
                "2022-04-11T00:00:00Z",
                "2022-04-12T00:00:00Z",
                "2022-04-14T00:00:00Z",
            ],
            "post",
        ),
        (
            "2122-04-01T00:00:00Z",  # Wednesday
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
                "2122-04-02T00:00:00Z",
                "2122-04-06T00:00:00Z",
                "2122-04-07T00:00:00Z",
                "2122-04-09T00:00:00Z",
                "2122-04-13T00:00:00Z",
                "2122-04-14T00:00:00Z",
            ],
            "put",
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
    activity_method: str,
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
            activity_method=activity_method,
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
    activity["startDate"] = start_date
    activity["timeOfDay"] = time_of_day
    activity["repeatDayFlags"] = repeat_day_flags

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity,
            weeks=weeks,
            activity_method=activity_method,
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
