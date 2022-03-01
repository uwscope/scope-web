from contextlib import nullcontext as does_not_raise
import datetime
import pytest
import scope.database.date_utils as date_utils


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (datetime.datetime(2019, 11, 1, 12, 0, 0), "2019-11-01T12:00:00Z"),
        (datetime.datetime(2019, 11, 1, 12, 59, 0), "2019-11-01T12:59:00Z"),
        (datetime.datetime(2019, 11, 1, 12, 59, 58), "2019-11-01T12:59:58Z"),
        (datetime.datetime(2019, 11, 1, 0, 0, 0), "2019-11-01T00:00:00Z"),
        (datetime.datetime(2019, 11, 1, 12, 0), "2019-11-01T12:00:00Z"),
    ],
)
def test_format_datetime(test_input, expected):
    assert date_utils.format_datetime(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("2019-11-01T12:00:00Z", datetime.datetime(2019, 11, 1, 12, 0, 0)),
        ("2019-11-01T12:59:00Z", datetime.datetime(2019, 11, 1, 12, 59, 0)),
        ("2019-11-01T12:59:58Z", datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ("2019-11-01T00:00:00Z", datetime.datetime(2019, 11, 1, 0, 0, 0)),
        ("2019-11-1T12:00:00Z", datetime.datetime(2019, 11, 1, 12, 0)),
        ("2019-11-01T12:59:58.0Z", datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ("2019-11-01T12:59:58.00Z", datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ("2019-11-01T12:59:58.000Z", datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ("2019-11-01T12:59:58.0000Z", datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ("2019-11-01T12:59:58.00000Z", datetime.datetime(2019, 11, 1, 12, 59, 58)),
        ("2019-11-01T12:59:58.000000Z", datetime.datetime(2019, 11, 1, 12, 59, 58)),
    ],
)
def test_parse_datetime(test_input, expected):
    assert date_utils.parse_datetime(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("2019-11-01T12:69:00Z", pytest.raises(ValueError)),
        ("2019-11-01T12:59:00", pytest.raises(ValueError)),
        ("2019-11-01U12:00:00Z", pytest.raises(ValueError)),
        ("2019-11-01T12:00:00Z", does_not_raise()),
    ],
)
def test_parse_datetime_failure(test_input, expected):
    with expected:
        assert date_utils.parse_datetime(test_input) is not None


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (datetime.datetime(2019, 11, 1, 12, 0, 0), "2019-11-01T00:00:00Z"),
        (datetime.datetime(2019, 11, 1, 12, 59, 0), "2019-11-01T00:00:00Z"),
        (datetime.datetime(2019, 11, 1, 12, 59, 58), "2019-11-01T00:00:00Z"),
        (datetime.datetime(2019, 11, 1, 0, 0, 0), "2019-11-01T00:00:00Z"),
        (datetime.datetime(2019, 11, 1, 12, 0), "2019-11-1T00:00:00Z"),
    ],
)
def test_format_date(test_input, expected):
    assert date_utils.format_date(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("2019-11-01T00:00:00Z", datetime.datetime(2019, 11, 1, 0, 0, 0)),
        ("2019-02-28T00:00:00Z", datetime.datetime(2019, 2, 28, 0, 0, 0)),
        ("2019-1-1T00:00:00Z", datetime.datetime(2019, 1, 1, 0, 0, 0)),
        ("2019-11-01T00:00:00Z", datetime.datetime(2019, 11, 1, 0, 0, 0)),
        ("2019-11-1T00:00:00Z", datetime.datetime(2019, 11, 1, 0, 0)),
    ],
)
def test_parse_date(test_input, expected):
    assert date_utils.parse_date(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("2019-11-01T12:00:00Z", pytest.raises(ValueError)),
        ("2019-11-01T12:59:00Z", pytest.raises(ValueError)),
        ("2019-11-01T12:59:58Z", pytest.raises(ValueError)),
        ("2019-11-1T12:00:00Z", pytest.raises(ValueError)),
        ("2019-11-1T00:00:00Z", does_not_raise()),
    ],
)
def test_parse_date_failure(test_input, expected):
    with expected:
        assert date_utils.parse_date(test_input) is not None
