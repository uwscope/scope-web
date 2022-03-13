import datetime as _datetime
import pytz
from typing import Union

DATETIME_FORMAT_COMPLETE = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_FORMAT_NO_MICROSECONDS = "%Y-%m-%dT%H:%M:%SZ"


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
        raise_on_not_datetime_utc_aware(datetime=date)

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

    raise_on_not_datetime_utc_aware(datetime=datetime)

    return datetime.strftime(DATETIME_FORMAT_NO_MICROSECONDS)


def raise_on_not_date(date: _datetime.date) -> None:
    """
    Raise if a provided date is not a date.
    """

    # datetime is also a date
    if isinstance(date, _datetime.datetime):
        raise ValueError("date must be date.")
    if not isinstance(date, _datetime.date):
        raise ValueError("date must be date.")


def raise_on_not_datetime_utc_aware(datetime: _datetime.datetime) -> None:
    """
    Raise if a provided datetime is not a datetime, not aware, or not in UTC.
    """

    if not isinstance(datetime, _datetime.datetime):
        raise ValueError("datetime must be datetime that is UTC aware.")
    if datetime.tzinfo is None:
        raise ValueError("datetime must be datetime that is UTC aware.")
    if datetime.tzinfo.utcoffset(datetime).total_seconds() != 0:
        raise ValueError("datetime must be datetime that is UTC aware.")
