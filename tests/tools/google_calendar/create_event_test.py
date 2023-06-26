import unittest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError
from datetime import datetime, timedelta
from superagi.tools.google_calendar.create_calendar_event import CreateEventCalendarInput, CreateEventCalendarTool
from superagi.helper.google_calendar_creds import GoogleCalendarCreds
from superagi.helper.calendar_date import CalendarDate

class TestCreateEventCalendarInput(unittest.TestCase):
    def test_create_event_calendar_input_valid(self):
        input_data = {
            "event_name": "Test Event",
            "description": "A test event.",
            "start_date": "2022-01-01",
            "start_time": "12:00:00",
            "end_date": "2022-01-01",
            "end_time": "13:00:00",
            "attendees": ["test@example.com"],
            "location": "London"
        }
        try:
            CreateEventCalendarInput(**input_data)
        except ValidationError:
            self.fail("ValidationError raised with valid input_data")

    def test_create_event_calendar_input_invalid(self):
        input_data = {
            "event_name": "Test Event",
            "description": "A test event.",
            "start_date": "2022-99-99",
            "start_time": "12:60:60",
            "end_date": "2022-99-99",
            "end_time": "13:60:60",
            "attendees": ["test@example.com"],
            "location": "London"
        }
        with self.assertRaises(ValidationError):
            CreateEventCalendarInput(**input_data)

class TestCreateEventCalendarTool(unittest.TestCase):
    def setUp(self):
        self.create_event_tool = CreateEventCalendarTool()
    @patch.object(GoogleCalendarCreds, "get_credentials")
    @patch.object(CalendarDate, "create_event_dates")

    def test_execute(self, mock_create_event_dates, mock_get_credentials):
        mock_get_credentials.return_value = {
            "success": True,
            "service": MagicMock()
        }
        mock_date_utc = {
            "start_datetime_utc": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "end_datetime_utc": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            "timeZone": "UTC"
        }
        mock_create_event_dates.return_value = mock_date_utc
        mock_service = MagicMock()
        mock_service.events.return_value = MagicMock()
        output_str_expected = f"Event Test Event at {mock_date_utc['start_datetime_utc']} created successfully, link for the event {'https://somerandomlink'}"
        output_str = self.create_event_tool._execute("Test Event", "A test event", ["test@example.com"], start_date="2022-01-01", start_time="12:00:00", end_date="2022-01-01", end_time="13:00:00", location="London")
        self.assertEqual(output_str, output_str_expected)
        event = {
            "summary": "Test Event",
            "description": "A test event",
            "start": {
                "dateTime": mock_date_utc["start_datetime_utc"],
                "timeZone": mock_date_utc["timeZone"]
            },
            "end": {
                "dateTime": mock_date_utc["end_datetime_utc"],
                "timeZone": mock_date_utc["timeZone"]
            },
            "attendees": [{"email": "test@example.com"}],
            "location": "London"
        }
        mock_get_credentials.assert_called_once()
        mock_create_event_dates.assert_called_once_with(mock_service, "2022-01-01", "12:00:00", "2022-01-01", "13:00:00")
        mock_service.events().insert.assert_called_once_with(calendarId="primary", body=event, conferenceDataVersion=1)

if __name__ == "__main__":
    unittest.main()