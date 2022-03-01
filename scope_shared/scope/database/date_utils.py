import datetime as _datetime
from typing import Union


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def parse_date(date: str) -> _datetime.date:
    """
    Parse date string from our date format.
    """
    parsed_date = _datetime.datetime.strptime(date, DATETIME_FORMAT)

    if (parsed_date.hour, parsed_date.minute, parsed_date.second) != (0, 0, 0):
        raise ValueError(
            "time data {} does not match format '%Y-%m-%dT00:00:00Z".format(date)
        )

    return parsed_date


def parse_datetime(datetime: str) -> _datetime.datetime:
    """
    Parse date string from our datetime format.
    """
    return _datetime.datetime.strptime(datetime, DATETIME_FORMAT)


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
