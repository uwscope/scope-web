import datetime
from typing import Union


DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def parse_datetime(date: str) -> Union[datetime.date, datetime.datetime]:
    """
    Parse date string into our datetime format.
    """
    return datetime.datetime.strptime(date, DATE_TIME_FORMAT)


def parse_date(date: str) -> Union[datetime.date, datetime.datetime]:
    """
    Parse date string into our date format.
    """
    parsed_date = datetime.datetime.strptime(date, DATE_TIME_FORMAT)

    if (parsed_date.hour, parsed_date.minute, parsed_date.second) != (0, 0, 0):
        raise ValueError("%H:%M:%S must be 00:00:00")

    return parsed_date


def format_date(date: Union[datetime.date, datetime.datetime]) -> str:
    """
    Format the date portion of a datetime into our standard format.
    """

    # Ensure a datetime.date object
    if isinstance(date, datetime.datetime):
        date = date.date()

    date = datetime.datetime.combine(
        date,
        datetime.datetime.min.time(),  # 00:00.00.00
    )

    return "{}Z".format(date.isoformat())


def format_datetime(date: datetime.datetime) -> str:
    """
    Format a datetime into our standard format.
    """

    return "{}Z".format(date.isoformat())
