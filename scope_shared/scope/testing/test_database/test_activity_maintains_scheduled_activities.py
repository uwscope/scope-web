"""
In addition to its standard set properties,
a put and post to scope.database.patient.activities must maintain the scheduled activities.
"""

import datetime
import pytest
import pytz
from typing import Callable

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.scheduled_activities
import scope.database.patients
import scope.database.patient_unsafe_utils as patient_unsafe_utils
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.enums
import scope.testing.fixtures_database_temp_patient


def test_activity_calculate_scheduled_activities_to_create():
    time_of_day = 8
    scheduled_activities = (
        scope.database.patient.activities._calculate_scheduled_activities_to_create(
            activity_id="testActivityId",
            activity={
                "name": "testActivityName",
                "isActive": True,
                "isDeleted": False,
                "startDateTime": date_utils.format_datetime(
                    pytz.utc.localize(datetime.datetime(2022, 3, 12, 6))
                ),
                "hasRepetition": True,
                "repeatDayFlags": {
                    scope.enums.DayOfWeek.Monday.value: True,
                    scope.enums.DayOfWeek.Tuesday.value: True,
                    scope.enums.DayOfWeek.Wednesday.value: False,
                    scope.enums.DayOfWeek.Thursday.value: False,
                    scope.enums.DayOfWeek.Friday.value: False,
                    scope.enums.DayOfWeek.Saturday.value: False,
                    scope.enums.DayOfWeek.Sunday.value: False,
                },
                "timeOfDay": time_of_day,
                "hasReminder": True,
                "reminderTimeOfDay": time_of_day,
            },
            maintenance_datetime=pytz.utc.localize(datetime.datetime(2022, 3, 14, 10)),
        )
    )
    scheduled_dates = []
    scheduled_dates.extend(
        [datetime.date(2022, 3, day) for day in list([14, 15, 21, 22, 28, 29])]
    )
    scheduled_dates.extend(
        [datetime.date(2022, 4, day) for day in list([4, 5, 11, 12, 18, 19, 25, 26])]
    )
    scheduled_dates.extend(
        [
            datetime.date(2022, 5, day)
            for day in list([2, 3, 9, 10, 16, 17, 23, 24, 30, 31])
        ]
    )
    scheduled_dates.extend(
        [datetime.date(2022, 6, day) for day in list([6, 7, 13, 14])]
    )

    assert scheduled_activities == [
        {
            "_type": "scheduledActivity",
            "activityId": "testActivityId",
            "activityName": "testActivityName",
            "completed": False,
            "dueDate": date_utils.format_date(scheduled_date_current),
            "dueTimeOfDay": time_of_day,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    datetime.datetime(
                        scheduled_date_current.year,
                        scheduled_date_current.month,
                        scheduled_date_current.day,
                        15,
                    )
                )
            ),
            "reminderDate": date_utils.format_date(scheduled_date_current),
            "reminderTimeOfDay": time_of_day,
            "reminderDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    datetime.datetime(
                        scheduled_date_current.year,
                        scheduled_date_current.month,
                        scheduled_date_current.day,
                        15,
                    )
                )
            ),
        }
        for scheduled_date_current in scheduled_dates
    ]
