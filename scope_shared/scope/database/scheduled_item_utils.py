import datetime as _datetime
import dateutil.relativedelta
import dateutil.rrule
import pytz
from typing import List, Optional

import scope.database.date_utils as date_utils
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils


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
    datetime = _datetime.datetime.combine(date, _datetime.time(hour=time_of_day))

    localized_datetime = timezone.localize(datetime)

    utc_datetime = localized_datetime.astimezone(pytz.utc)

    return utc_datetime


def _initial_date(
    *,
    start_date: _datetime.date,
    day_of_week: str,
) -> _datetime.date:
    return start_date + dateutil.relativedelta.relativedelta(
        weekday=DATEUTIL_WEEKDAYS_MAP[day_of_week]
    )


def _scheduled_dates(
    *,
    start_date: _datetime.date,
    day_of_week: str,
    frequency: str,
    months: int,
) -> List[_datetime.date]:
    initial_date: _datetime.date = _initial_date(
        start_date=start_date, day_of_week=day_of_week
    )
    until_date: _datetime.date = initial_date + dateutil.relativedelta.relativedelta(
        months=months
    )

    if frequency == scope.enums.ScheduledItemFrequency.Daily.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.DAILY, interval=1, dtstart=initial_date, until=until_date
        )
    elif frequency == scope.enums.ScheduledItemFrequency.Weekly.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.WEEKLY, interval=1, dtstart=initial_date, until=until_date
        )
    elif frequency == scope.enums.ScheduledItemFrequency.Biweekly.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.WEEKLY, interval=2, dtstart=initial_date, until=until_date
        )
    elif frequency == scope.enums.ScheduledItemFrequency.Monthly.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.WEEKLY, interval=4, dtstart=initial_date, until=until_date
        )
    else:
        raise ValueError()

    return [repeat_datetime.date() for repeat_datetime in repeat_rule]


def create_scheduled_items(
    *,
    start_date: _datetime.date,
    day_of_week: str,
    frequency: str,
    due_time_of_day: int,
    reminder: bool,
    reminder_time_of_day: Optional[int] = None,
    timezone: pytz.timezone,
    months: int,
) -> List[dict]:
    """
    Create a list of scheduled items based on a schedule.
    """
    date_utils.raise_on_not_date(start_date)
    if due_time_of_day < 0 or due_time_of_day > 23:
        raise ValueError("due_time_of_day must be int >=0 and <= 23")
    if reminder:
        if reminder is None or reminder_time_of_day < 0 or reminder_time_of_day > 23:
            raise ValueError("reminder_time_of_day must be int >=0 and <= 23")
    if timezone.zone not in pytz.all_timezones:
        raise ValueError("timezone must be valid pytz timezone")

    scheduled_dates = _scheduled_dates(
        start_date=start_date,
        day_of_week=day_of_week,
        frequency=frequency,
        months=months,
    )

    result_scheduled_items = []
    for scheduled_date_current in scheduled_dates:
        scheduled_item_current = {}

        scheduled_item_current.update(
            {
                "dueDate": date_utils.format_date(scheduled_date_current),
                "dueTimeOfDay": due_time_of_day,
                "dueDateTime": date_utils.format_datetime(
                    _localized_datetime(
                        date=scheduled_date_current,
                        time_of_day=due_time_of_day,
                        timezone=timezone,
                    )
                ),
            }
        )

        if reminder:
            scheduled_item_current.update(
                {
                    "reminderDate": date_utils.format_date(scheduled_date_current),
                    "reminderTimeOfDay": reminder_time_of_day,
                    "reminderDateTime": date_utils.format_datetime(
                        _localized_datetime(
                            date=scheduled_date_current,
                            time_of_day=reminder_time_of_day,
                            timezone=timezone,
                        )
                    ),
                }
            )

        scheduled_item_current["completed"] = False

        schema_utils.raise_for_invalid_schema(
            data=scheduled_item_current, schema=scope.schema.scheduled_item_schema
        )

        result_scheduled_items.append(scheduled_item_current)

    return result_scheduled_items


def pending_scheduled_items(
    *,
    scheduled_items: List[dict],
    after_datetime: _datetime.datetime,
) -> List[dict]:
    """
    Pending items are those which are:
    - Not already completed
    - In the future

    Pending items will generally be deleted and replaced due to a change in the schedule.
    """

    date_utils.raise_on_not_datetime_utc_aware(after_datetime)

    result_pending_scheduled_items = []
    for scheduled_item_current in scheduled_items:
        schema_utils.raise_for_invalid_schema(
            data=scheduled_item_current, schema=scope.schema.scheduled_item_schema
        )

        pending = not scheduled_item_current["completed"]
        if pending:
            pending = (
                date_utils.parse_datetime(scheduled_item_current["dueDateTime"])
                > after_datetime
            )

        if pending:
            result_pending_scheduled_items.append(scheduled_item_current)

    return result_pending_scheduled_items
