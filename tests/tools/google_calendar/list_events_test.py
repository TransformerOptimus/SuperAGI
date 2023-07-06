import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from pydantic import ValidationError
from superagi.tools.google_calendar.list_calendar_events import ListCalendarEventsInput, ListCalendarEventsTool
from superagi.helper.google_calendar_creds import GoogleCalendarCreds
from superagi.helper.calendar_date import CalendarDate

class TestListCalendarEventsInput(unittest.TestCase):
    
    def test_valid_input(self):
        input_data = {
            "start_time": "20:00:00",
            "start_date": "2022-11-10",
            "end_date": "2022-11-11",
            "end_time": "22:00:00",
        }
        try:
            ListCalendarEventsInput(**input_data)
            validation_passed = True
        except ValidationError:
            validation_passed = False
        self.assertEqual(validation_passed, True)
    
    def test_invalid_input(self):
        input_data = {
            "start_time": "invalid time",
            "start_date": "invalid date",
            "end_date": "another invalid date",
            "end_time": "another invalid time",
        }
        with self.assertRaises(ValidationError):
            ListCalendarEventsInput(**input_data)

class TestListCalendarEventsTool(unittest.TestCase):
    @patch.object(GoogleCalendarCreds, 'get_credentials')
    @patch.object(CalendarDate, 'get_date_utc')
    
    def test_without_events(self, mock_get_date_utc, mock_get_credentials):
        tool = ListCalendarEventsTool()
        mock_get_credentials.return_value = {
            "success": True,
            "service": MagicMock()
        }
        mock_service = mock_get_credentials()["service"]
        mock_service.events().list().execute.return_value = {}
        mock_get_date_utc.return_value = {
            'start_datetime_utc': datetime.now().isoformat(),
            'end_datetime_utc': datetime.now().isoformat()
        }
        result = tool._execute('20:00:00', '2022-11-10', '2022-11-11', '22:00:00')
        self.assertEqual(result, "No events found for the given date and time range.")

if __name__ == "__main__":
    unittest.main()









