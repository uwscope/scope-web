import datetime
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.scheduled_activities
import scope.schema
import scope.schema_utils as schema_utils


def _create_scheduled_activities_assertions(scheduled_activities: List[dict]) -> None:
    schema_utils.assert_schema(
        data=scheduled_activities,
        schema=scope.schema.scheduled_activities_schema,
    )
    for scheduled_activity_current in scheduled_activities:
        assert not scheduled_activity_current["completed"]
        assert scheduled_activity_current["dueType"] == "Exact"


# TODO: Discuss w/ James if this can parametrized.
def test_create_scheduled_activities(
    data_fake_activity_factory: Callable[[], dict],
):
    activity = data_fake_activity_factory()
    # Assume activity has just been inserted into db using POST
    # create_scheduled_activities method needs activity to have its SEMANTIC_SET_ID
    activity[
        scope.database.patient.activities.SEMANTIC_SET_ID
    ] = collection_utils.generate_set_id()

    # OPTION 1 - hasRepetition is False
    activity["hasRepetition"] = False
    start_date = datetime.date.today()
    time_of_day = 8
    activity["startDate"] = date_utils.format_date(start_date)
    activity["timeOfDay"] = time_of_day
    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity
        )
    )
    assert len(scheduled_activities) == 1
    assert scheduled_activities[0]["dueDate"] == date_utils.format_datetime(
        datetime.datetime.combine(start_date, datetime.time(hour=time_of_day))
    )
    _create_scheduled_activities_assertions(scheduled_activities=scheduled_activities)

    # OPTION 2 - hasRepetition is False and hasReminder is False
    activity["hasRepetition"] = False
    activity["hasReminder"] = False
    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity
        )
    )
    assert len(scheduled_activities) == 1
    assert scheduled_activities[0]["dueDate"] == date_utils.format_datetime(
        datetime.datetime.combine(start_date, datetime.time(hour=time_of_day))
    )
    assert scheduled_activities[0]["reminder"] == None
    _create_scheduled_activities_assertions(scheduled_activities=scheduled_activities)

    # OPTION 3 - hasRepetition is False and hasReminder is True
    activity["hasRepetition"] = False
    activity["hasReminder"] = True
    reminder_time_of_day = 8
    activity["reminderTimeOfDay"] = reminder_time_of_day
    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity
        )
    )
    assert len(scheduled_activities) == 1
    assert scheduled_activities[0]["dueDate"] == date_utils.format_datetime(
        datetime.datetime.combine(start_date, datetime.time(hour=time_of_day))
    )
    assert scheduled_activities[0]["reminder"] == date_utils.format_datetime(
        datetime.datetime.combine(start_date, datetime.time(hour=reminder_time_of_day))
    )
    _create_scheduled_activities_assertions(scheduled_activities=scheduled_activities)

    # TODO: hasRepetition is True left.
