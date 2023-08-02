import unittest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from superagi.tools.google_calendar.delete_calendar_event import DeleteCalendarEventInput, DeleteCalendarEventTool

class TestDeleteCalendarEventInput(unittest.TestCase):
    def test_valid_input(self):
        input_data = {"event_id": "123456"}
        input_obj = DeleteCalendarEventInput(**input_data)
        self.assertEqual(input_obj.event_id, "123456")

    def test_invalid_input(self):
        input_data = {"event_id": ""}
        with self.assertRaises(ValidationError):
            DeleteCalendarEventInput(**input_data)

class TestDeleteCalendarEventTools(unittest.TestCase):
    def setUp(self):
        self.delete_tool = DeleteCalendarEventTool()
    @patch("your_module.GoogleCalendarCreds")

    def test_execute_delete_event_with_valid_id(self, mock_google_calendar_creds):
        credentials_obj = Mock()
        credentials_obj.get_credentials.return_value = {"success": True, "service": Mock()}
        mock_google_calendar_creds.return_value = credentials_obj
        self.assertEqual(self.delete_tool._execute("123456"), "Event Successfully deleted from your Google Calendar")
    @patch("your_module.GoogleCalendarCreds")

    def test_execute_delete_event_with_no_id(self, mock_google_calendar_creds):
        self.assertEqual(self.delete_tool._execute("None"), "Add Event ID to delete an event from Google Calendar")
    @patch("your_module.GoogleCalendarCreds")

    def test_execute_delete_event_with_no_credentials(self, mock_google_calendar_creds):
        credentials_obj = Mock()
        credentials_obj.get_credentials.return_value = {"success": False}
        mock_google_calendar_creds.return_value = credentials_obj
        self.assertEqual(self.delete_tool._execute("123456"), "Kindly connect to Google Calendar")

if __name__ == "__main__":
    unittest.main()