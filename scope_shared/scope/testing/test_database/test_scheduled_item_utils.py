import datetime as _datetime
import dateutil.rrule
import pprint
import pytest
import pytz

import scope.database.date_utils as date_utils
import scope.database.scheduled_item_utils
import scope.enums


_REPEAT_DAY_FLAGS_TUE_THU_FRI = {
    scope.enums.DayOfWeek.Monday.value: False,
    scope.enums.DayOfWeek.Tuesday.value: True,
    scope.enums.DayOfWeek.Wednesday.value: False,
    scope.enums.DayOfWeek.Thursday.value: True,
    scope.enums.DayOfWeek.Friday.value: True,
    scope.enums.DayOfWeek.Saturday.value: False,
    scope.enums.DayOfWeek.Sunday.value: False,
}


def test_scheduled_item_convert_byweekday():
    for (repeat_day_flags, expected) in [
        (  # Every day of the week
            {
                scope.enums.DayOfWeek.Monday.value: True,
                scope.enums.DayOfWeek.Tuesday.value: True,
                scope.enums.DayOfWeek.Wednesday.value: True,
                scope.enums.DayOfWeek.Thursday.value: True,
                scope.enums.DayOfWeek.Friday.value: True,
                scope.enums.DayOfWeek.Saturday.value: True,
                scope.enums.DayOfWeek.Sunday.value: True,
            },
            (
                dateutil.rrule.MO,
                dateutil.rrule.TU,
                dateutil.rrule.WE,
                dateutil.rrule.TH,
                dateutil.rrule.FR,
                dateutil.rrule.SA,
                dateutil.rrule.SU,
            ),
        ),
        (  # Every day of the week except Tuesday
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,
            (
                dateutil.rrule.TU,
                dateutil.rrule.TH,
                dateutil.rrule.FR,
            ),
        ),
    ]:
        assert (
            scope.database.scheduled_item_utils._convert_byweekday(
                repeat_day_flags=repeat_day_flags
            )
            == expected
        )


def test_scheduled_item_localized_datetime():
    for (date, time_of_day, timezone, expected) in [
        (
            _datetime.date(2021, 9, 1),
            7,
            pytz.utc,
            "2021-09-01T07:00:00Z",
        ),
        (
            _datetime.date(2021, 9, 1),
            7,
            pytz.timezone("America/Los_Angeles"),
            "2021-09-01T14:00:00Z",
        ),
        (
            _datetime.date(2021, 9, 1),
            7,
            pytz.timezone("America/New_York"),
            "2021-09-01T11:00:00Z",
        ),
    ]:
        assert (
            date_utils.format_datetime(
                datetime=scope.database.scheduled_item_utils._localized_datetime(
                    date=date,
                    time_of_day=time_of_day,
                    timezone=timezone,
                )
            )
            == expected
        )


def test_scheduled_item_initial_date():
    for (
        start_date,
        effective_date,
        frequency,
        repeat_day_flags,
        day_of_week,
        expected_date,
    ) in [
        (  # Daily item, effective the same day
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 11),
            scope.enums.ScheduledItemFrequency.Daily.value,
            None,
            None,
            _datetime.date(2022, 3, 11),
        ),
        (  # Daily item, effective in the past
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 1),
            scope.enums.ScheduledItemFrequency.Daily.value,
            None,
            None,
            _datetime.date(2022, 3, 11),
        ),
        (  # Daily item, effective in the future
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 4, 1),
            scope.enums.ScheduledItemFrequency.Daily.value,
            None,
            None,
            _datetime.date(2022, 4, 1),
        ),
        (  # Weekly item, with repeat day flags, effective the same day
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 11),
            scope.enums.ScheduledItemFrequency.Weekly.value,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,
            None,
            _datetime.date(2022, 3, 11),
        ),
        (  # Weekly item, with repeat day flags, effective in the past
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 1),
            scope.enums.ScheduledItemFrequency.Weekly.value,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,
            None,
            _datetime.date(2022, 3, 11),
        ),
        (  # Weekly item, with repeat day flags, effective in the future
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 4, 1),
            scope.enums.ScheduledItemFrequency.Weekly.value,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,
            None,
            _datetime.date(2022, 4, 1),
        ),
        (  # Weekly item, with day of week, effective the same day
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 11),
            scope.enums.ScheduledItemFrequency.Weekly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 3, 16),
        ),
        (  # Weekly item, with day of week, effective in the past
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 1),
            scope.enums.ScheduledItemFrequency.Weekly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 3, 16),
        ),
        (  # Weekly item, with day of week, effective in the future
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 4, 1),
            scope.enums.ScheduledItemFrequency.Weekly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 4, 6),
        ),
        (  # Biweekly item, with day of week, effective the same day
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 11),
            scope.enums.ScheduledItemFrequency.Biweekly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 3, 16),
        ),
        (  # Biweekly item, with day of week, effective in the past
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 1),
            scope.enums.ScheduledItemFrequency.Biweekly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 3, 16),
        ),
        (  # Biweekly item, with day of week, effective in the future
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 4, 1),
            scope.enums.ScheduledItemFrequency.Biweekly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 4, 13),
        ),
        (  # Monthly item, with day of week, effective the same day
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 11),
            scope.enums.ScheduledItemFrequency.Monthly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 3, 16),
        ),
        (  # Monthly item, with day of week, effective in the past
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 1),
            scope.enums.ScheduledItemFrequency.Monthly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 3, 16),
        ),
        (  # Monthly item, with day of week, effective in the future
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 4, 1),
            scope.enums.ScheduledItemFrequency.Monthly.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,
            _datetime.date(2022, 4, 13),
        ),
    ]:
        initial_date = scope.database.scheduled_item_utils._initial_date(
            start_date=start_date,
            effective_date=effective_date,
            frequency=frequency,
            repeat_day_flags=repeat_day_flags,
            day_of_week=day_of_week,
        )

        if initial_date != expected_date:
            pprint.pprint(
                {
                    "start_date": start_date,
                    "effective_date": effective_date,
                    "frequency": frequency,
                    "repeat_day_flags": repeat_day_flags,
                    "day_of_week": day_of_week,
                    "expected_date": expected_date,
                }
            )

            assert initial_date == expected_date


def test_scheduled_item_scheduled_dates():
    for (
        start_date,
        effective_date,
        has_repetition,
        frequency,
        repeat_day_flags,
        day_of_week,
        months,
        expected,
    ) in [
        (  # No repetition
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 18),
            False,
            None,
            None,
            None,
            None,
            [_datetime.date(2022, 3, 11)],
        ),
        (
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 18),
            True,
            scope.enums.ScheduledItemFrequency.Daily.value,
            None,
            None,
            1,
            (
                [_datetime.date(2022, 3, day) for day in range(18, 31 + 1)]
                + [_datetime.date(2022, 4, day) for day in range(1, 18 + 1)]
            ),
        ),
        (  # Weekly repetition based on day_of_week
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 18),
            True,
            scope.enums.ScheduledItemFrequency.Weekly.value,
            None,
            scope.enums.DayOfWeek.Monday.value,
            1,
            [
                _datetime.date(2022, 3, 21),
                _datetime.date(2022, 3, 28),
                _datetime.date(2022, 4, 4),
                _datetime.date(2022, 4, 11),
                _datetime.date(2022, 4, 18),
            ],
        ),
        (  # Weekly repetition based on repeat_day_flags
            _datetime.date(2022, 3, 16),  # Wednesday
            _datetime.date(2022, 3, 18),
            True,
            scope.enums.ScheduledItemFrequency.Weekly.value,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,
            None,
            1,
            [
                _datetime.date(2022, 3, 18),
                _datetime.date(2022, 3, 22),
                _datetime.date(2022, 3, 24),
                _datetime.date(2022, 3, 25),
                _datetime.date(2022, 3, 29),
                _datetime.date(2022, 3, 31),
                _datetime.date(2022, 4, 1),
                _datetime.date(2022, 4, 5),
                _datetime.date(2022, 4, 7),
                _datetime.date(2022, 4, 8),
                _datetime.date(2022, 4, 12),
                _datetime.date(2022, 4, 14),
                _datetime.date(2022, 4, 15),
            ],
        ),
        (
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 18),
            True,
            scope.enums.ScheduledItemFrequency.Biweekly.value,
            None,
            scope.enums.DayOfWeek.Monday.value,
            1,
            [
                _datetime.date(2022, 3, 28),
                _datetime.date(2022, 4, 11),
                _datetime.date(2022, 4, 25),
            ],
        ),
        (
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 18),
            True,
            scope.enums.ScheduledItemFrequency.Monthly.value,
            None,
            scope.enums.DayOfWeek.Monday.value,
            1,
            [
                _datetime.date(2022, 4, 11),
                _datetime.date(2022, 5, 9),
            ],
        ),
        (
            _datetime.date(2022, 3, 11),  # Friday
            _datetime.date(2022, 3, 18),
            True,
            scope.enums.ScheduledItemFrequency.Monthly.value,
            None,
            scope.enums.DayOfWeek.Monday.value,
            3,
            [
                _datetime.date(2022, 4, 11),
                _datetime.date(2022, 5, 9),
                _datetime.date(2022, 6, 6),
                _datetime.date(2022, 7, 4),
            ],
        ),
    ]:
        assert (
            scope.database.scheduled_item_utils._scheduled_dates(
                start_date=start_date,
                effective_date=effective_date,
                has_repetition=has_repetition,
                frequency=frequency,
                repeat_day_flags=repeat_day_flags,
                day_of_week=day_of_week,
                months=months,
            )
            == expected
        )


def test_scheduled_item_scheduled_dates_valueerror():
    for (
        start_date,
        effective_date,
        has_repetition,
        frequency,
        repeat_day_flags,
        day_of_week,
        months,
    ) in [
        (  # start_date is not date
            _datetime.datetime(2022, 3, 11, 0, 0, 7),
            _datetime.date(2022, 3, 11),
            False,
            None,
            None,
            None,
            None,
        ),
        (  # effective_date is not date
            _datetime.date(2022, 3, 11),
            _datetime.datetime(2022, 3, 11, 0, 0, 7),
            False,
            None,
            None,
            None,
            None,
        ),
        (  # has_repetition is False, repetition variables must be None
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            False,
            scope.enums.ScheduledItemFrequency.Daily,  # None
            None,
            None,
            None,
        ),
        (  # has_repetition is False, repetition variables must be None
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            False,
            None,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,  # None
            None,
            None,
        ),
        (  # has_repetition is False, repetition variables must be None
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            False,
            None,
            None,
            scope.enums.DayOfWeek.Wednesday.value,  # None
            None,
        ),
        (  # has_repetition is False, repetition variables must be None
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            False,
            None,
            None,
            None,
            3,  # None
        ),
        (  # has_repetition is True, must provide frequency
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            None,  # Missing
            None,
            None,
            None,
        ),
        (  # has_repetition is True, must provide months
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Daily,
            None,
            None,
            None,  # Missing
        ),
        (  # frequency is Daily, repeat_day_flags and day_of_week must be None
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Daily.value,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,  # None
            None,
            3,
        ),
        (  # frequency is Daily, repeat_day_flags and day_of_week must be None
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Daily.value,
            None,
            scope.enums.DayOfWeek.Wednesday.value,  # None
            3,
        ),
        (  # frequency is Weekly, must provide exactly one of day variables
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Weekly.value,
            None,  # Exactly one
            None,  # Exactly one
            3,
        ),
        (  # frequency is Weekly, must provide exactly one of day variables
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Weekly.value,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,  # Exactly one
            scope.enums.DayOfWeek.Wednesday.value,  # Exactly one
            3,
        ),
        (  # frequency is Biweekly, repeat_day_flags must be None
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Biweekly.value,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,  # None
            scope.enums.DayOfWeek.Wednesday.value,
            3,
        ),
        (  # frequency is Biweekly, must provide day_of_week
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Biweekly.value,
            None,
            None,  # Missing
            3,
        ),
        (  # frequency is Monthly, repeat_day_flags must be None
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Monthly.value,
            _REPEAT_DAY_FLAGS_TUE_THU_FRI,  # None
            None,
            3,
        ),
        (  # frequency is Monthly, must provide day_of_week
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Monthly.value,
            None,
            None,  # Missing
            3,
        ),
        (  # repeat_day_flags is provided, at least one flag must be True
            _datetime.date(2022, 3, 11),
            _datetime.date(2022, 3, 11),
            True,
            scope.enums.ScheduledItemFrequency.Weekly.value,
            {
                day_of_week_item.value: False
                for day_of_week_item in scope.enums.DayOfWeek
            },
            None,
            3,
        ),
    ]:
        with pytest.raises(ValueError):
            scope.database.scheduled_item_utils._scheduled_dates(
                start_date=start_date,
                effective_date=effective_date,
                has_repetition=has_repetition,
                frequency=frequency,
                repeat_day_flags=repeat_day_flags,
                day_of_week=day_of_week,
                months=months,
            )

            # Only reached if ValueError was not raised
            pprint.pprint(
                {
                    "start_date": start_date,
                    "has_repetition": has_repetition,
                    "frequency": frequency,
                    "repeat_day_flags": repeat_day_flags,
                    "day_of_week": day_of_week,
                    "months": months,
                }
            )


def test_scheduled_item_create_scheduled_items_no_reminder():
    scheduled_items = scope.database.scheduled_item_utils.create_scheduled_items(
        start_datetime=pytz.timezone("America/Los_Angeles")
        .localize(_datetime.datetime(2022, 3, 11, 14))
        .astimezone(pytz.utc),
        effective_datetime=pytz.timezone("America/Los_Angeles")
        .localize(_datetime.datetime(2022, 4, 1, 14))
        .astimezone(pytz.utc),
        has_repetition=True,
        frequency=scope.enums.ScheduledItemFrequency.Biweekly.value,
        repeat_day_flags=None,
        day_of_week=scope.enums.DayOfWeek.Monday.value,
        due_time_of_day=8,
        reminder=False,
        timezone=pytz.timezone("America/Los_Angeles"),
        months=3,
    )

    assert scheduled_items == [
        {
            "completed": False,
            "dueDate": "2022-04-11T00:00:00Z",
            "dueDateTime": "2022-04-11T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-04-25T00:00:00Z",
            "dueDateTime": "2022-04-25T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-05-09T00:00:00Z",
            "dueDateTime": "2022-05-09T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-05-23T00:00:00Z",
            "dueDateTime": "2022-05-23T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-06-06T00:00:00Z",
            "dueDateTime": "2022-06-06T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-06-20T00:00:00Z",
            "dueDateTime": "2022-06-20T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-07-04T00:00:00Z",
            "dueDateTime": "2022-07-04T15:00:00Z",
            "dueTimeOfDay": 8,
        },
    ]


def test_scheduled_item_create_scheduled_items_with_reminder():
    scheduled_items = scope.database.scheduled_item_utils.create_scheduled_items(
        start_datetime=pytz.timezone("America/Los_Angeles")
        .localize(_datetime.datetime(2022, 3, 11, 14))
        .astimezone(pytz.utc),
        effective_datetime=pytz.timezone("America/Los_Angeles")
        .localize(_datetime.datetime(2022, 4, 1, 14))
        .astimezone(pytz.utc),
        has_repetition=True,
        frequency=scope.enums.ScheduledItemFrequency.Biweekly.value,
        repeat_day_flags=None,
        day_of_week=scope.enums.DayOfWeek.Monday.value,
        due_time_of_day=8,
        reminder=True,
        reminder_time_of_day=6,
        timezone=pytz.timezone("America/Los_Angeles"),
        months=3,
    )

    assert scheduled_items == [
        {
            "completed": False,
            "dueDate": "2022-04-11T00:00:00Z",
            "dueDateTime": "2022-04-11T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-04-11T00:00:00Z",
            "reminderDateTime": "2022-04-11T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
        {
            "completed": False,
            "dueDate": "2022-04-25T00:00:00Z",
            "dueDateTime": "2022-04-25T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-04-25T00:00:00Z",
            "reminderDateTime": "2022-04-25T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
        {
            "completed": False,
            "dueDate": "2022-05-09T00:00:00Z",
            "dueDateTime": "2022-05-09T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-05-09T00:00:00Z",
            "reminderDateTime": "2022-05-09T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
        {
            "completed": False,
            "dueDate": "2022-05-23T00:00:00Z",
            "dueDateTime": "2022-05-23T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-05-23T00:00:00Z",
            "reminderDateTime": "2022-05-23T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
        {
            "completed": False,
            "dueDate": "2022-06-06T00:00:00Z",
            "dueDateTime": "2022-06-06T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-06-06T00:00:00Z",
            "reminderDateTime": "2022-06-06T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
        {
            "completed": False,
            "dueDate": "2022-06-20T00:00:00Z",
            "dueDateTime": "2022-06-20T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-06-20T00:00:00Z",
            "reminderDateTime": "2022-06-20T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
        {
            "completed": False,
            "dueDate": "2022-07-04T00:00:00Z",
            "dueDateTime": "2022-07-04T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-07-04T00:00:00Z",
            "reminderDateTime": "2022-07-04T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
    ]


def test_scheduled_item_pending_items():
    scheduled_items = [
        {
            "completed": True,  # Completed item in past, should not be pending
            "dueDate": "2022-03-14T00:00:00Z",
            "dueDateTime": "2022-03-14T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,  # Incomplete item in past, should not be pending
            "dueDate": "2022-03-28T00:00:00Z",
            "dueDateTime": "2022-03-28T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,  # Incomplete item in past, should not be pending
            "dueDate": "2022-04-11T00:00:00Z",
            "dueDateTime": "2022-04-11T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": True,  # Completed item in future, should not be pending
            "dueDate": "2022-04-25T00:00:00Z",
            "dueDateTime": "2022-04-25T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,  # Incomplete item in future, should be pending
            "dueDate": "2022-05-09T00:00:00Z",
            "dueDateTime": "2022-05-09T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,  # Incomplete item in future, should be pending
            "dueDate": "2022-05-23T00:00:00Z",
            "dueDateTime": "2022-05-23T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,  # Incomplete item in future, should be pending
            "dueDate": "2022-06-06T00:00:00Z",
            "dueDateTime": "2022-06-06T15:00:00Z",
            "dueTimeOfDay": 8,
        },
    ]

    pending_items = scope.database.scheduled_item_utils.pending_scheduled_items(
        scheduled_items=scheduled_items,
        after_datetime=pytz.utc.localize(_datetime.datetime(2022, 4, 18)),
    )

    assert pending_items == [
        {
            "completed": False,
            "dueDate": "2022-05-09T00:00:00Z",
            "dueDateTime": "2022-05-09T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-05-23T00:00:00Z",
            "dueDateTime": "2022-05-23T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-06-06T00:00:00Z",
            "dueDateTime": "2022-06-06T15:00:00Z",
            "dueTimeOfDay": 8,
        },
    ]
