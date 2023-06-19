import unittest
from unittest import mock

from fastapi import HTTPException

from superagi.controllers.tool_config import update_tool_config, ToolKit
from superagi.models.tool_config import ToolConfig
from superagi.models.db import connect_db
from sqlalchemy.orm import sessionmaker

# from your_app import db  # Assuming you have imported the necessary modules

engine = connect_db()
Session = sessionmaker(bind=engine)
session = Session()

class ToolConfigTestCase(unittest.TestCase):
    @mock.patch('your_app.ToolKit.get_tool_kit_from_name')
    @mock.patch('your_app.db.session')
    def test_update_tool_config_successful(self, mock_session, mock_get_tool_kit_from_name):
        # Mock the necessary dependencies
        mock_tool_kit = mock.Mock(id=1)
        mock_get_tool_kit_from_name.return_value = mock_tool_kit
        mock_tool_config = mock.Mock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_tool_config

        # Define the test data
        tool_kit_name = 'example_tool_kit'
        configs = [
            {"key": "config1", "value": "value1"},
            {"key": "config2", "value": "value2"}
        ]

        # Invoke the method
        response = update_tool_config(tool_kit_name, configs)

        # Assert the response
        self.assertEqual(response, {"message": "Tool configs updated successfully"})

        # Assert the mock method calls
        mock_get_tool_kit_from_name.assert_called_once_with(session, tool_kit_name)
        mock_session.query.return_value.filter_by.assert_any_call(tool_kit_id=mock_tool_kit.id, key='config1')
        mock_session.query.return_value.filter_by.assert_any_call(tool_kit_id=mock_tool_kit.id, key='config2')
        mock_tool_config.__setattr__.assert_any_call('value', 'value1')
        mock_tool_config.__setattr__.assert_any_call('value', 'value2')
        mock_session.commit.assert_called_once()

    def test_update_tool_config_tool_kit_not_found(self):
        # Mock the necessary dependencies
        mock_get_tool_kit_from_name = mock.Mock(return_value=None)

        # Define the test data
        tool_kit_name = 'non_existent_tool_kit'
        configs = [{"key": "config1", "value": "value1"}]

        # Invoke the method and assert the exception
        with self.assertRaises(HTTPException) as context:
            update_tool_config(tool_kit_name, configs)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Tool kit not found")

    def test_update_tool_config_unexpected_error(self):
        # Mock the necessary dependencies
        mock_get_tool_kit_from_name = mock.Mock(side_effect=Exception("Unexpected error"))
        mock_session = mock.Mock()
        mock_session.commit.side_effect = Exception("Commit error")

        # Define the test data
        tool_kit_name = 'example_tool_kit'
        configs = [{"key": "config1", "value": "value1"}]

        # Invoke the method and assert the exception
        with self.assertRaises(HTTPException) as context:
            update_tool_config(tool_kit_name, configs)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Unexpected error")

    # Add more test methods to cover different scenarios and edge cases

if __name__ == '__main__':
    unittest.main()
