import datetime as _datetime
import dateutil.relativedelta
import dateutil.rrule
import pytz
from typing import List, Dict, Optional, Tuple

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


def _convert_byweekday(repeat_day_flags: dict) -> Tuple:
    """
    Convert our repeat day flags format into the byweekday format expected by dateutil.
    """

    byweekday = []
    for day, day_flag in repeat_day_flags.items():
        if day_flag:
            byweekday.append(DATEUTIL_WEEKDAYS_MAP[day])

    return tuple(byweekday)


def _localized_datetime(
    *,
    date: _datetime.date,
    time_of_day: int,
    timezone: pytz.timezone,
) -> _datetime.datetime:
    """
    Obtain an absolute datetime corresponding to:
    - a provided date
    - a provided time_of_day
    - a provided timezone

    The datetime will correspond to the above, but will be UTC aware.
    """

    datetime = _datetime.datetime.combine(date, _datetime.time(hour=time_of_day))

    localized_datetime = timezone.localize(datetime)

    utc_datetime = localized_datetime.astimezone(pytz.utc)

    return utc_datetime


def _initial_date(
    *,
    start_date: _datetime.date,
    effective_date: _datetime.date,
    frequency: str,
    repeat_day_flags: Optional[Dict[str, bool]],
    day_of_week: Optional[str],
) -> _datetime.date:
    # TODO: This could account for a patient's history with this scheduled item

    # If a start date is after an effective date,
    # we can treat the start date as an effective date.
    # This simplifies the resulting logic.
    if start_date > effective_date:
        effective_date = start_date

    if frequency == scope.enums.ScheduledItemFrequency.Daily.value:
        # Happens every day, so it can begin on the effective date
        initial_date = effective_date
    elif frequency == scope.enums.ScheduledItemFrequency.Weekly.value:
        # Happens on the same day(s) every week
        # Find the first such day on/after the effective date
        if repeat_day_flags:
            initial_date = None
            for (day_of_week, flag) in repeat_day_flags.items():
                if flag:
                    initial_date_current = (
                        effective_date
                        + dateutil.relativedelta.relativedelta(
                            weekday=DATEUTIL_WEEKDAYS_MAP[day_of_week]
                        )
                    )

                    if initial_date is None or initial_date_current < initial_date:
                        initial_date = initial_date_current
        else:  # Use day_of_week
            initial_date = effective_date + dateutil.relativedelta.relativedelta(
                weekday=DATEUTIL_WEEKDAYS_MAP[day_of_week]
            )
    elif frequency == scope.enums.ScheduledItemFrequency.Biweekly.value:
        # Beginning with start_date, happens on day_of_week every two weeks
        # Find the first such day on/after the effective date
        initial_date = start_date + dateutil.relativedelta.relativedelta(
            weekday=DATEUTIL_WEEKDAYS_MAP[day_of_week]
        )
        while initial_date < effective_date:
            initial_date = initial_date + dateutil.relativedelta.relativedelta(weeks=2)
    elif frequency == scope.enums.ScheduledItemFrequency.Monthly.value:
        # Beginning with start_date, happens on day_of_week every four weeks
        # Find the first such day on/after the effective date
        initial_date = start_date + dateutil.relativedelta.relativedelta(
            weekday=DATEUTIL_WEEKDAYS_MAP[day_of_week]
        )
        while initial_date < effective_date:
            initial_date = initial_date + dateutil.relativedelta.relativedelta(weeks=4)
    else:
        raise ValueError()

    return initial_date


def _scheduled_dates(
    *,
    start_date: _datetime.date,  # Scheduled date of first/only item
    has_repetition: bool,  # Whether to repeat
    effective_date: _datetime.date,  # Date from which we want to schedule
    frequency: Optional[str],  # Frequency to repeat
    repeat_day_flags: Optional[dict],  # For weekly frequency, days of week to repeat
    day_of_week: Optional[
        str
    ],  # For frequencies beyond weekly, day of week to start/repeat
    months: Optional[int],  # How many months of items to generate
) -> List[_datetime.date]:
    #
    # Check allowable parameter combinations
    #
    date_utils.raise_on_not_date(date=start_date)
    date_utils.raise_on_not_date(date=effective_date)
    if not has_repetition:
        if any(
            [
                frequency is not None,
                repeat_day_flags is not None,
                day_of_week is not None,
                months is not None,
            ]
        ):
            raise ValueError(
                "If has_repetition is False, repetition variables must be None"
            )
    if has_repetition:
        if frequency is None:
            raise ValueError("If has_repetition is True, frequency must be provided")
        if months is None:
            raise ValueError("If has_repetition is True, months must be provided")
    if frequency is scope.enums.ScheduledItemFrequency.Daily.value:
        if any([repeat_day_flags is not None, day_of_week is not None]):
            raise ValueError(
                "If frequency is Daily, repeat_day_flags and day_of_week must be None"
            )
    elif frequency is scope.enums.ScheduledItemFrequency.Weekly.value:
        day_variable_count = 0
        if repeat_day_flags is not None:
            day_variable_count += 1
        if day_of_week is not None:
            day_variable_count += 1

        if day_variable_count != 1:
            raise ValueError(
                "If frequency is Weekly, either repeat_day_flags or day_of_week must be provided"
            )
    elif frequency in [
        scope.enums.ScheduledItemFrequency.Biweekly.value,
        scope.enums.ScheduledItemFrequency.Monthly.value,
    ]:
        if repeat_day_flags is not None:
            raise ValueError(
                "If frequency is Biweekly or Monthly, repeat_day_flags must be None"
            )
        if day_of_week is None:
            raise ValueError(
                "If frequency is Biweekly or Monthly, day_of_week must be provided"
            )
    if repeat_day_flags is not None:
        if not any(repeat_day_flags.values()):
            raise ValueError("At least one repeat_day_flag must be True")

    #
    # If there was no repetition, the start_date is our one and only date.
    #
    if not has_repetition:
        return [start_date]

    #
    # Calculate our first occurrence on/after both the start date and the effective date
    #
    initial_date: _datetime.date = _initial_date(
        start_date=start_date,
        effective_date=effective_date,
        frequency=frequency,
        repeat_day_flags=repeat_day_flags,
        day_of_week=day_of_week,
    )

    until_date: _datetime.date = initial_date + dateutil.relativedelta.relativedelta(
        months=months
    )

    if frequency == scope.enums.ScheduledItemFrequency.Daily.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.DAILY,
            interval=1,
            dtstart=initial_date,
            until=until_date,
        )
    elif frequency == scope.enums.ScheduledItemFrequency.Weekly.value:
        if repeat_day_flags:
            repeat_rule = dateutil.rrule.rrule(
                dateutil.rrule.WEEKLY,
                dtstart=initial_date,
                until=until_date,
                byweekday=_convert_byweekday(repeat_day_flags),
            )
        else:
            repeat_rule = dateutil.rrule.rrule(
                dateutil.rrule.WEEKLY,
                interval=1,
                dtstart=initial_date,
                until=until_date,
            )
    elif frequency == scope.enums.ScheduledItemFrequency.Biweekly.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.WEEKLY,
            interval=2,
            dtstart=initial_date,
            until=until_date,
        )
    elif frequency == scope.enums.ScheduledItemFrequency.Monthly.value:
        repeat_rule = dateutil.rrule.rrule(
            dateutil.rrule.WEEKLY,
            interval=4,
            dtstart=initial_date,
            until=until_date,
        )
    else:
        raise ValueError()

    return [repeat_datetime.date() for repeat_datetime in repeat_rule]


def create_scheduled_items(
    *,
    start_datetime: _datetime.datetime,
    effective_datetime: _datetime.datetime,
    has_repetition: bool,
    frequency: str,
    repeat_day_flags: Optional[dict],
    day_of_week: Optional[str],
    due_time_of_day: int,
    reminder: bool,
    reminder_time_of_day: Optional[int] = None,
    timezone: pytz.timezone,
    months: int,
) -> List[dict]:
    """
    Create a list of scheduled items based on a schedule.
    """
    date_utils.raise_on_not_datetime_utc_aware(start_datetime)
    date_utils.raise_on_not_datetime_utc_aware(effective_datetime)
    if due_time_of_day < 0 or due_time_of_day > 23:
        raise ValueError("due_time_of_day must be int >=0 and <= 23")
    if reminder:
        if reminder is None or reminder_time_of_day < 0 or reminder_time_of_day > 23:
            raise ValueError("reminder_time_of_day must be int >=0 and <= 23")
    if timezone.zone not in pytz.all_timezones:
        raise ValueError("timezone must be valid pytz timezone")

    # Obtain a start date in the patient's scheduling time zone
    start_date = start_datetime.astimezone(timezone).date()
    effective_date = effective_datetime.astimezone(timezone).date()
    scheduled_dates = _scheduled_dates(
        start_date=start_date,
        effective_date=effective_date,
        has_repetition=has_repetition,
        repeat_day_flags=repeat_day_flags,
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
    - After the provided datetime

    For example, pending items may be deleted and replaced due to a change in the schedule.
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
