from superagi.helper.time_helper import get_time_difference, parse_interval_to_seconds
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock


def test_parse_interval_to_seconds():
    assert parse_interval_to_seconds("2 Minutes") == 120
    assert parse_interval_to_seconds("3 Hours") == 10800
    assert parse_interval_to_seconds("1 Days") == 86400
    assert parse_interval_to_seconds("7 Weeks") == 4233600
    assert parse_interval_to_seconds("2 Months") == 5184000
