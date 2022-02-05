import datetime
from typing import Union


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
