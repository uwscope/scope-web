import datetime as _datetime
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
        raise ValueError(
            "time data {} does not match format '%Y-%m-%dT00:00:00Z".format(date)
        )

    parsed_date = parsed_datetime

    return parsed_date


def parse_datetime(datetime: str) -> _datetime.datetime:
    """
    Parse date string from our datetime format.
    """

    try:
        return _datetime.datetime.strptime(datetime, DATETIME_FORMAT_NO_MICROSECONDS)
    except ValueError:
        pass

    return _datetime.datetime.strptime(datetime, DATETIME_FORMAT_COMPLETE)


def format_date(date: Union[_datetime.date, _datetime.datetime]) -> str:
    """
    Format the date portion of a datetime into our format.
    """

    # Ensure a datetime.date object
    if isinstance(date, _datetime.datetime):
        date = date.date()

    date = _datetime.datetime.combine(
        date,
        _datetime.datetime.min.time(),  # 00:00.00.00
    )

    return "{}Z".format(date.isoformat())


def format_datetime(datetime: _datetime.datetime) -> str:
    """
    Format a datetime into our format.
    """

    return "{}Z".format(datetime.isoformat())
