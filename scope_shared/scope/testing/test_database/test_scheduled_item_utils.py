import datetime as _datetime
import pytz
import scope.database.date_utils
import scope.database.scheduled_item_utils


def test_scheduled_item_compute_localized_datetime():
    for (date, time_of_day, timezone, expected) in [
        (
            _datetime.date(2021, 9, 1),
            7,
            pytz.utc,
            "2021-09-01T07:00:00Z"
        ),
        (
                _datetime.date(2021, 9, 1),
                7,
                pytz.timezone("America/Los_Angeles"),
                "2021-09-01T14:00:00Z"
        ),
        (
                _datetime.date(2021, 9, 1),
                7,
                pytz.timezone("America/New_York"),
                "2021-09-01T11:00:00Z"
        ),
    ]:
        assert scope.database.date_utils.format_datetime(
            datetime=scope.database.scheduled_item_utils.compute_localized_datetime(
                date=date,
                time_of_day=time_of_day,
                timezone=timezone,
            )
        ) == expected
