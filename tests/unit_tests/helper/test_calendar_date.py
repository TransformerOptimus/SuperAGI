import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone
import pytz
from dateutil import tz
from superagi.helper import CalendarDate

class TestCalendarDate(unittest.TestCase):
    def setUp(self):
        self.cd = CalendarDate()
        self.service = MagicMock()
        self.service.calendars().get().execute.return_value = {'timeZone': 'Asia/Kolkata'}

    def test_get_time_zone(self):
        time_zone = self.cd.get_time_zone(self.service)
        self.assertEqual(time_zone, 'Asia/Kolkata')

    def test_convert_to_utc(self):
        date_time = datetime(2022, 1, 1, 0, 0, 0)
        local_tz = pytz.timezone('Asia/Kolkata')
        utc_datetime = self.cd.convert_to_utc(date_time, local_tz)
        self.assertEqual(utc_datetime, datetime(2022, 1, 1, 5, 0, tzinfo=timezone.utc))

    def test_string_to_datetime(self):
        date_str = '2022-01-01'
        date_format = '%Y-%m-%d'
        date_obj = datetime.strptime(date_str, date_format)
        self.assertEqual(date_obj, self.cd.string_to_datetime(date_str, date_format))

    def test_localize_daterange(self):
        start_date, end_date = '2022-01-01', '2022-01-02'
        start_time, end_time = '10:00:00', '12:00:00'
        local_tz = pytz.timezone('Asia/Kolkata')
        start_datetime_utc, end_datetime_utc = self.cd.localize_daterange(start_date, end_date, start_time, end_time, local_tz)

        self.assertEqual(start_datetime_utc, datetime(2022, 1, 1, 15, 0, tzinfo=timezone.utc))
        self.assertEqual(end_datetime_utc, datetime(2022, 1, 2, 17, 0, tzinfo=timezone.utc))

    def test_datetime_to_string(self):
        date_time = datetime(2022, 1, 1, 0, 0, 0)
        date_format = '%Y-%m-%d'
        date_str = '2022-01-01'
        self.assertEqual(date_str, self.cd.datetime_to_string(date_time, date_format))

    def test_get_date_utc(self):
        start_date, end_date = '2022-01-01', '2022-01-02'
        start_time, end_time = '10:00:00', '12:00:00'
        date_utc = {
            "start_datetime_utc": "2022-01-01T15:00:00.000000Z",
            "end_datetime_utc": "2022-01-02T17:00:00.000000Z"
        }
        result = self.cd.get_date_utc(start_date, end_date, start_time, end_time, self.service)
        self.assertEqual(date_utc, result)

    def test_create_event_dates(self):
        start_date, end_date = '2022-01-01', '2022-01-02'
        start_time, end_time = '10:00:00', '12:00:00'
        date_utc = {
            "start_datetime_utc": "2022-01-01T15:00:00.000000Z",
            "end_datetime_utc": "2022-01-02T17:00:00.000000Z",
            "timeZone": "Asia/Kolkata"
        }
        result = self.cd.create_event_dates(self.service, start_date, start_time, end_date, end_time)
        self.assertEqual(date_utc, result)

if __name__ == '__main__':
    unittest.main()