import datetime as _datetime
import dateutil.rrule
import pytz
from typing import Union

import scope.enums

DATETIME_FORMAT_COMPLETE = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_FORMAT_NO_MICROSECONDS = "%Y-%m-%dT%H:%M:%SZ"
DATEUTIL_WEEKDAYS_MAP = {
    scope.enums.DayOfWeek.Monday.value: dateutil.rrule.MO,
    scope.enums.DayOfWeek.Tuesday.value: dateutil.rrule.TU,
    scope.enums.DayOfWeek.Wednesday.value: dateutil.rrule.WE,
    scope.enums.DayOfWeek.Thursday.value: dateutil.rrule.TH,
    scope.enums.DayOfWeek.Friday.value: dateutil.rrule.FR,
    scope.enums.DayOfWeek.Saturday.value: dateutil.rrule.SA,
    scope.enums.DayOfWeek.Sunday.value: dateutil.rrule.SU,
}


def parse_date(date: str) -> _datetime.date:
    """
    Parse date string from our date format.
    """
    parsed_datetime = parse_datetime(date)

    if any(
        [
            parsed_datetime.hour != 0,
            parsed_datetime.minute != 0,
            parsed_datetime.second != 0,
        ]
    ):
        raise ValueError('Invalid date format: "{}".'.format(date))

    parsed_date = parsed_datetime

    return parsed_date


def parse_datetime(datetime: str) -> _datetime.datetime:
    """
    Parse date string from our datetime format.
    """

    parsed_naive_datetime = None

    try:
        parsed_naive_datetime = _datetime.datetime.strptime(
            datetime,
            DATETIME_FORMAT_NO_MICROSECONDS,
        )
    except ValueError:
        pass

    try:
        parsed_naive_datetime = _datetime.datetime.strptime(
            datetime,
            DATETIME_FORMAT_COMPLETE,
        )
    except ValueError:
        pass

    if not parsed_naive_datetime:
        raise ValueError('Invalid datetime format: "{}".'.format(datetime))

    return pytz.utc.localize(parsed_naive_datetime)


def format_date(date: Union[_datetime.date, _datetime.datetime]) -> str:
    """
    Format the date portion of a datetime into our format.
    """

    if isinstance(date, _datetime.datetime):
        raise_on_datetime_not_utc_aware(datetime=date)

        # Ensure a datetime.date object
        date = date.date()

    # Convert date into a datetime with 0 values
    date = _datetime.datetime.combine(
        date,
        _datetime.datetime.min.time(),  # 00:00.00.00
    )
    date = pytz.utc.localize(date)

    return date.strftime(DATETIME_FORMAT_NO_MICROSECONDS)


def format_datetime(datetime: _datetime.datetime) -> str:
    """
    Format a datetime into our format.
    """

    raise_on_datetime_not_utc_aware(datetime=datetime)

    return datetime.strftime(DATETIME_FORMAT_NO_MICROSECONDS)


def raise_on_datetime_not_utc_aware(datetime: _datetime.datetime) -> None:
    """
    Raise if a provided datetime is not aware or not in UTC.
    """

    if not isinstance(datetime, _datetime.datetime):
        raise ValueError("datetime must be UTC aware.")
    if datetime.tzinfo is None:
        raise ValueError("datetime must be UTC aware.")
    if datetime.tzinfo.utcoffset(datetime).total_seconds() != 0:
        raise ValueError("datetime must be UTC aware.")

