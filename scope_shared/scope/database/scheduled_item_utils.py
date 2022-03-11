import datetime as _datetime
import dateutil.relativedelta
import dateutil.rrule
import pytz
from typing import List

import scope.database.date_utils as date_utils
import scope.enums


DATEUTIL_WEEKDAYS_MAP = {
    scope.enums.DayOfWeek.Monday.value: dateutil.rrule.MO,
    scope.enums.DayOfWeek.Tuesday.value: dateutil.rrule.TU,
    scope.enums.DayOfWeek.Wednesday.value: dateutil.rrule.WE,
    scope.enums.DayOfWeek.Thursday.value: dateutil.rrule.TH,
    scope.enums.DayOfWeek.Friday.value: dateutil.rrule.FR,
    scope.enums.DayOfWeek.Saturday.value: dateutil.rrule.SA,
    scope.enums.DayOfWeek.Sunday.value: dateutil.rrule.SU,
}


def _localized_datetime(
    *,
    date: _datetime.date,
    time_of_day: int,
    timezone: pytz.timezone,
) -> _datetime.datetime:
    date_utils.raise_on_not_date(date)
    if time_of_day < 0 or time_of_day > 23:
        raise ValueError("time_of_day must be int >=0 and <= 23")
    if timezone.zone not in pytz.all_timezones:
        raise ValueError("timezone must be valid pytz timezone")

    datetime = _datetime.datetime.combine(
        date,
        _datetime.time(hour=time_of_day)
    )

    localized_datetime = timezone.localize(datetime)

    utc_datetime = localized_datetime.astimezone(pytz.utc)

    return utc_datetime


def _initial_date(
    *,
    start_date: _datetime.date,
    day_of_week: str,
) -> _datetime.date:
    return start_date + dateutil.relativedelta.relativedelta(weekday=DATEUTIL_WEEKDAYS_MAP[day_of_week])


def _scheduled_dates(
    *,
    start_date: _datetime.date,
    day_of_week: str,
    frequency: str,
    months: int,
) -> List[_datetime.date]:
    initial_date: _datetime.date = _initial_date(start_date=start_date, day_of_week=day_of_week)
    until_date: _datetime.date = initial_date + dateutil.relativedelta.relativedelta(months=months)

    if frequency == scope.enums.ScheduledItemFrequency.Daily.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.DAILY,
            interval=1,
            dtstart=initial_date,
            until=until_date
        )
    elif frequency == scope.enums.ScheduledItemFrequency.Weekly.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.WEEKLY,
            interval=1,
            dtstart=initial_date,
            until=until_date
        )
    elif frequency == scope.enums.ScheduledItemFrequency.Biweekly.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.WEEKLY,
            interval=2,
            dtstart=initial_date,
            until=until_date
        )
    elif frequency == scope.enums.ScheduledItemFrequency.Monthly.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.WEEKLY,
            interval=4,
            dtstart=initial_date,
            until=until_date
        )
    else:
        raise ValueError()

    return [repeat_datetime.date() for repeat_datetime in repeat_rule]
