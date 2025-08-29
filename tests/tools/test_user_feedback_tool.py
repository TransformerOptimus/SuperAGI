# In tests/tools/test_user_feedback_tool.py

import unittest
from unittest.mock import patch
from superagi.tools.user_feedback_tool import UserFeedbackTool

class TestUserFeedbackTool(unittest.TestCase):

    def test_execute_with_user_input(self):
        """Test that the tool correctly captures and returns user input."""
        # Arrange
        tool = UserFeedbackTool()
        simulated_user_input = "This is my test feedback"

        # Act: We use 'patch' to pretend the user typed something in the console.
        with patch('builtins.input', return_value=simulated_user_input):
            result = tool._execute()

        # Assert
        expected_output = f"User provided the following feedback: {simulated_user_input}"
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()