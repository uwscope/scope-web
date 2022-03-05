from contextlib import nullcontext as does_not_raise
import datetime
import pytest
import pytz
import scope.database.date_utils as date_utils


def test_datetime_is_default_naive():
    test_date = datetime.datetime(2019, 11, 1, 12, 0, 0)

    assert test_date.tzinfo is None


def test_parsed_datetime_is_utc_aware():
    test_datetime = date_utils.parse_datetime(datetime="2019-11-01T12:59:58Z")

    assert test_datetime.tzinfo is not None
    assert test_datetime.tzinfo.utcoffset(test_datetime).total_seconds() == 0


def test_format_datetime():
    for (test_input, expected) in [
        (
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 12, 59, 58)),
            "2019-11-01T12:59:58Z",
        ),
    ]:
        assert date_utils.format_datetime(test_input) == expected


def test_format_datetime_failure():
    for test_input in [
        datetime.date(2019, 11, 1),
        pytz.timezone("US/Pacific").localize(datetime.datetime(2019, 11, 1, 12, 0)),
    ]:
        with pytest.raises(ValueError):
            date_utils.format_datetime(test_input)


def test_parse_datetime():
    for (test_input, expected) in [
        (
            "2019-11-01T12:59:58Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ),
        (
            "2019-11-01T00:00:00Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 0, 0, 0)),
        ),
        (
            "2019-11-1T00:00:00Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 0, 0, 0)),
        ),
        (
            "2019-11-01T12:59:58.000Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ),
        (
            "2019-11-01T12:59:58.000000Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ),
    ]:
        assert date_utils.parse_datetime(test_input) == expected


def test_parse_datetime_failure():
    for test_input in [
        "2019-11-01T12:12:12",
        "2019-11-01U12:12:12Z",
        "2019-11-01T70:12:12Z",
        "2019-11-01T12:70:12Z",
        "2019-11-01T12:12:70Z",
    ]:
        with pytest.raises(ValueError):
            date_utils.parse_datetime(test_input)


def test_format_date():
    for (test_input, expected) in [
        (
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 12, 0, 0)),
            "2019-11-01T00:00:00Z",
        ),
        (
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 12, 59, 0)),
            "2019-11-01T00:00:00Z",
        ),
        (
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 12, 59, 58)),
            "2019-11-01T00:00:00Z",
        ),
        (
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 0, 0, 0)),
            "2019-11-01T00:00:00Z",
        ),
        (
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 12, 0)),
            "2019-11-01T00:00:00Z",
        ),
    ]:
        assert date_utils.format_date(test_input) == expected


def test_parse_date():
    for (test_input, expected) in [
        (
            "2019-11-01T00:00:00Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 0, 0, 0)),
        ),
        (
            "2019-02-28T00:00:00Z",
            pytz.utc.localize(datetime.datetime(2019, 2, 28, 0, 0, 0)),
        ),
        (
            "2019-1-1T00:00:00Z",
            pytz.utc.localize(datetime.datetime(2019, 1, 1, 0, 0, 0)),
        ),
        (
            "2019-11-01T00:00:00Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 0, 0, 0)),
        ),
        (
            "2019-11-1T00:00:00Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 0, 0)),
        ),
        (
            "2019-11-1T00:00:00.000Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 0, 0)),
        ),
        (
            "2019-11-1T00:00:00.000000Z",
            pytz.utc.localize(datetime.datetime(2019, 11, 1, 0, 0)),
        ),
    ]:
        assert date_utils.parse_date(test_input) == expected


def test_parse_date_failure():
    for test_input in [
        ("2019-11-01T12:00:00Z"),
        ("2019-11-01T00:12:00Z"),
        ("2019-11-01T00:00:12Z"),
        ("2019-11-1T12:00:00Z"),
    ]:
        with pytest.raises(ValueError):
            date_utils.parse_date(test_input)
