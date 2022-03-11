import datetime as _datetime
import pprint

import pytz

import scope.database.date_utils
import scope.database.scheduled_item_utils
import scope.enums


def test_scheduled_item_localized_datetime():
    for (date, time_of_day, timezone, expected) in [
        (
            _datetime.date(2021, 9, 1),
            7,
            pytz.utc,
            "2021-09-01T07:00:00Z"
        ),
        (
            _datetime.date(2021, 9, 1),
            7,
            pytz.timezone("America/Los_Angeles"),
            "2021-09-01T14:00:00Z"
        ),
        (
            _datetime.date(2021, 9, 1),
            7,
            pytz.timezone("America/New_York"),
            "2021-09-01T11:00:00Z"
        ),
    ]:
        assert scope.database.date_utils.format_datetime(
            datetime=scope.database.scheduled_item_utils._localized_datetime(
                date=date,
                time_of_day=time_of_day,
                timezone=timezone,
            )
        ) == expected


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
        assert scope.database.scheduled_item_utils._initial_date(
            start_date=date,
            day_of_week=day_of_week,
        ) == expected


def test_scheduled_item_scheduled_dates():
    for (start_date, day_of_week, frequency, months, expected) in [
        (
            _datetime.date(2022, 3, 11),  # Friday
            scope.enums.DayOfWeek.Monday.value,
            scope.enums.ScheduledItemFrequency.Daily.value,
            1,
            (
                [_datetime.date(2022, 3, day) for day in range(14, 31 + 1)] +
                [_datetime.date(2022, 4, day) for day in range(1, 14 + 1)]
            )
        ),
        (
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
            ]
        ),
        (
                _datetime.date(2022, 3, 11),  # Friday
                scope.enums.DayOfWeek.Monday.value,
                scope.enums.ScheduledItemFrequency.Biweekly.value,
                1,
                [
                    _datetime.date(2022, 3, 14),
                    _datetime.date(2022, 3, 28),
                    _datetime.date(2022, 4, 11),
                ]
        ),
        (
                _datetime.date(2022, 3, 11),  # Friday
                scope.enums.DayOfWeek.Monday.value,
                scope.enums.ScheduledItemFrequency.Monthly.value,
                1,
                [
                    _datetime.date(2022, 3, 14),
                    _datetime.date(2022, 4, 11),
                ]
        ),
        (
                _datetime.date(2022, 3, 11),  # Friday
                scope.enums.DayOfWeek.Monday.value,
                scope.enums.ScheduledItemFrequency.Monthly.value,
                3,
                [
                    _datetime.date(2022, 3, 14),
                    _datetime.date(2022, 4, 11),
                    _datetime.date(2022, 5, 9),
                    _datetime.date(2022, 6, 6),
                ]
        ),
    ]:
        assert scope.database.scheduled_item_utils._scheduled_dates(
            start_date=start_date,
            day_of_week=day_of_week,
            frequency=frequency,
            months=months,
        ) == expected
