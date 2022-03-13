import datetime as _datetime
import dateutil.rrule
import pytz

import scope.database.date_utils
import scope.database.scheduled_item_utils
import scope.enums


def test_scheduled_item_convert_byweekday():
    for (repeat_day_flags, expected) in [
        (   # Every day of the week
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
        (   # Every day of the week except Tuesday
            {
                scope.enums.DayOfWeek.Monday.value: True,
                scope.enums.DayOfWeek.Tuesday.value: False,
                scope.enums.DayOfWeek.Wednesday.value: True,
                scope.enums.DayOfWeek.Thursday.value: True,
                scope.enums.DayOfWeek.Friday.value: True,
                scope.enums.DayOfWeek.Saturday.value: True,
                scope.enums.DayOfWeek.Sunday.value: True,
            },
            (
                dateutil.rrule.MO,
                dateutil.rrule.WE,
                dateutil.rrule.TH,
                dateutil.rrule.FR,
                dateutil.rrule.SA,
                dateutil.rrule.SU,
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
            scope.database.date_utils.format_datetime(
                datetime=scope.database.scheduled_item_utils._localized_datetime(
                    date=date,
                    time_of_day=time_of_day,
                    timezone=timezone,
                )
            )
            == expected
        )


def test_scheduled_item_initial_date():
    for (date, day_of_week, expected) in [
        (
            _datetime.date(2022, 3, 11),  # Friday
            scope.enums.DayOfWeek.Friday.value,
            _datetime.date(2022, 3, 11),
        ),
        (
            _datetime.date(2022, 3, 11),  # Friday
            scope.enums.DayOfWeek.Monday.value,
            _datetime.date(2022, 3, 14),  # The following Monday
        ),
    ]:
        assert (
            scope.database.scheduled_item_utils._initial_date(
                start_date=date,
                day_of_week=day_of_week,
            )
            == expected
        )


def test_scheduled_item_scheduled_dates():
    for (
        has_repetition,
        repeat_day_flags,
        start_date,
        day_of_week,
        frequency,
        months,
        expected,
    ) in [
        (
            None,
            None,
            _datetime.date(2022, 3, 11),  # Friday
            scope.enums.DayOfWeek.Monday.value,
            scope.enums.ScheduledItemFrequency.Daily.value,
            1,
            (
                [_datetime.date(2022, 3, day) for day in range(14, 31 + 1)]
                + [_datetime.date(2022, 4, day) for day in range(1, 14 + 1)]
            ),
        ),
        (
            None,
            None,
            _datetime.date(2022, 3, 11),  # Friday
            scope.enums.DayOfWeek.Monday.value,
            scope.enums.ScheduledItemFrequency.Weekly.value,
            1,
            [
                _datetime.date(2022, 3, 14),
                _datetime.date(2022, 3, 21),
                _datetime.date(2022, 3, 28),
                _datetime.date(2022, 4, 4),
                _datetime.date(2022, 4, 11),
            ],
        ),
        (
            None,
            None,
            _datetime.date(2022, 3, 11),  # Friday
            scope.enums.DayOfWeek.Monday.value,
            scope.enums.ScheduledItemFrequency.Biweekly.value,
            1,
            [
                _datetime.date(2022, 3, 14),
                _datetime.date(2022, 3, 28),
                _datetime.date(2022, 4, 11),
            ],
        ),
        (
            None,
            None,
            _datetime.date(2022, 3, 11),  # Friday
            scope.enums.DayOfWeek.Monday.value,
            scope.enums.ScheduledItemFrequency.Monthly.value,
            1,
            [
                _datetime.date(2022, 3, 14),
                _datetime.date(2022, 4, 11),
            ],
        ),
        (
            None,
            None,
            _datetime.date(2022, 3, 11),  # Friday
            scope.enums.DayOfWeek.Monday.value,
            scope.enums.ScheduledItemFrequency.Monthly.value,
            3,
            [
                _datetime.date(2022, 3, 14),
                _datetime.date(2022, 4, 11),
                _datetime.date(2022, 5, 9),
                _datetime.date(2022, 6, 6),
            ],
        ),
    ]:
        assert (
            scope.database.scheduled_item_utils._scheduled_dates(
                has_repetition=has_repetition,
                repeat_day_flags=repeat_day_flags,
                start_date=start_date,
                day_of_week=day_of_week,
                frequency=frequency,
                months=months,
            )
            == expected
        )


def test_scheduled_item_create_scheduled_items_no_reminder():
    scheduled_items = scope.database.scheduled_item_utils.create_scheduled_items(
        has_repetition=None,
        repeat_day_flags=None,
        start_date=_datetime.date(2022, 3, 11),
        day_of_week=scope.enums.DayOfWeek.Monday.value,
        frequency=scope.enums.ScheduledItemFrequency.Biweekly.value,
        due_time_of_day=8,
        reminder=False,
        timezone=pytz.timezone("America/Los_Angeles"),
        months=3,
    )

    assert scheduled_items == [
        {
            "completed": False,
            "dueDate": "2022-03-14T00:00:00Z",
            "dueDateTime": "2022-03-14T15:00:00Z",
            "dueTimeOfDay": 8,
        },
        {
            "completed": False,
            "dueDate": "2022-03-28T00:00:00Z",
            "dueDateTime": "2022-03-28T15:00:00Z",
            "dueTimeOfDay": 8,
        },
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
    ]


def test_scheduled_item_create_scheduled_items_with_reminder():
    scheduled_items = scope.database.scheduled_item_utils.create_scheduled_items(
        has_repetition=None,
        repeat_day_flags=None,
        start_date=_datetime.date(2022, 3, 11),
        day_of_week=scope.enums.DayOfWeek.Monday.value,
        frequency=scope.enums.ScheduledItemFrequency.Biweekly.value,
        due_time_of_day=8,
        reminder=True,
        reminder_time_of_day=6,
        timezone=pytz.timezone("America/Los_Angeles"),
        months=3,
    )

    assert scheduled_items == [
        {
            "completed": False,
            "dueDate": "2022-03-14T00:00:00Z",
            "dueDateTime": "2022-03-14T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-03-14T00:00:00Z",
            "reminderDateTime": "2022-03-14T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
        {
            "completed": False,
            "dueDate": "2022-03-28T00:00:00Z",
            "dueDateTime": "2022-03-28T15:00:00Z",
            "dueTimeOfDay": 8,
            "reminderDate": "2022-03-28T00:00:00Z",
            "reminderDateTime": "2022-03-28T13:00:00Z",
            "reminderTimeOfDay": 6,
        },
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
