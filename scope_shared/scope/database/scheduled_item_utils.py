import datetime as _datetime
import pprint

import pytz

import scope.database.date_utils as date_utils


def compute_localized_datetime(
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
