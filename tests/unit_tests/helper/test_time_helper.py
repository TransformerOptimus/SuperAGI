from superagi.helper.time_helper import get_time_difference, parse_interval_to_seconds
import pytest

def test_get_time_difference():
    timestamp1 = "2023-06-26 17:31:08.884322"
    timestamp2 = "2023-06-27 03:57:42.038497"
    expected_result = {
        "years": 0,
        "months": 0,
        "days": 0,
        "hours": 10,
        "minutes": 26
    }
    assert get_time_difference(timestamp1, timestamp2) == expected_result



def test_parse_interval_to_seconds():
    assert parse_interval_to_seconds("2 Minutes") == 120
    assert parse_interval_to_seconds("3 Hours") == 10800
    assert parse_interval_to_seconds("1 Days") == 86400
    assert parse_interval_to_seconds("7 Weeks") == 4233600
    assert parse_interval_to_seconds("2 Months") == 5184000
