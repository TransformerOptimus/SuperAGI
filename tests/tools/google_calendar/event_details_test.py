import unittest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError
from superagi.tools.google_calendar.event_details_calendar import EventDetailsCalendarInput, EventDetailsCalendarTool
from superagi.helper.google_calendar_creds import GoogleCalendarCreds

class TestEventDetailsCalendarInput(unittest.TestCase):
    def test_invalid_input(self):
        with self.assertRaises(ValidationError):
            EventDetailsCalendarInput(event_id=None)
    
    def test_valid_input(self):
        input_data = EventDetailsCalendarInput(event_id="test_event_id")
        self.assertEqual(input_data.event_id, "test_event_id")

class TestEventDetailsCalendarTool(unittest.TestCase):
    def setUp(self):
        self.tool = EventDetailsCalendarTool()

    def test_no_credentials(self):
        with patch.object(GoogleCalendarCreds, 'get_credentials') as mock_get_credentials:
            mock_get_credentials.return_value = {"success": False}
            result = self.tool._execute(event_id="test_event_id")
            self.assertEqual(result, "Kindly connect to Google Calendar")

    def test_no_event_id(self):
        with patch.object(GoogleCalendarCreds, 'get_credentials') as mock_get_credentials:
            mock_get_credentials.return_value = {"success": True}
            result = self.tool._execute(event_id="None")
            self.assertEqual(result, "Add Event ID to fetch details of an event from Google Calendar")

    def test_valid_event(self):
        event_data = {
            'summary': 'Test Meeting',
            'start': {'dateTime': '2022-01-01T09:00:00'},
            'end': {'dateTime': '2022-01-01T10:00:00'},
            'attendees': [{'email': 'attendee1@example.com'},
                          {'email': 'attendee2@example.com'}]
        }
        with patch.object(GoogleCalendarCreds, 'get_credentials') as mock_get_credentials:
            with patch('your_module.base64.b64decode') as mock_b64decode:
                mock_get_credentials.return_value = {"success": True, "service": MagicMock()}
                service = mock_get_credentials.return_value["service"]
                service.events().get.return_value.execute.return_value = event_data
                mock_b64decode.return_value.decode.return_value = "decoded_event_id"
                result = self.tool._execute(event_id="test_event_id")
                mock_b64decode.assert_called_once_with("test_event_id")
                service.events().get.assert_called_once_with(calendarId="primary", eventId="decoded_event_id")
                expected_output = ("Event details for the event id 'test_event_id' is - \n"
                                   "Summary : Test Meeting\n"
                                   "Start Date and Time : 2022-01-01T09:00:00\n"
                                   "End Date and Time : 2022-01-01T10:00:00\n"
                                   "Attendees : attendee1@example.com,attendee2@example.com")
                self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()