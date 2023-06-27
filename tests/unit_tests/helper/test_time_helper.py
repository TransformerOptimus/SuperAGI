from superagi.helper.time_helper import get_time_difference


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
