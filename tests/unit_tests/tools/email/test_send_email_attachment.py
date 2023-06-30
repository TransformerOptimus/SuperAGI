import unittest
from unittest.mock import patch, Mock
import os
from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool, SendEmailAttachmentInput

class TestSendEmailAttachmentTool(unittest.TestCase):
    @patch("superagi.tools.email.send_email_attachment.SendEmailAttachmentTool.send_email_with_attachment")
    @patch("superagi.helper.resource_helper.ResourceHelper.get_agent_resource_path")
    @patch("superagi.helper.resource_helper.ResourceHelper.get_root_input_dir")
    @patch("os.path.exists")
    def test__execute(self, mock_exists, mock_get_root_input_dir, mock_get_agent_resource_path, mock_send_email_with_attachment):
        # Arrange
        tool = SendEmailAttachmentTool()
        tool.agent_id = 1
        mock_exists.return_value = True
        mock_get_agent_resource_path.return_value = "/test/path/test.txt"
        mock_get_root_input_dir.return_value = "/root_dir/"
        mock_send_email_with_attachment.return_value = "Email sent"
        expected_result = "Email sent"

        # Act
        result = tool._execute("test@example.com", "test subject", "test body", "test.txt")

        # Assert
        self.assertEqual(result, expected_result)
        mock_get_agent_resource_path.assert_called_once_with("test.txt", tool.agent_id)
        mock_send_email_with_attachment.assert_called_once_with("test@example.com", "test subject", "test body", "/test/path/test.txt", "test.txt")

if __name__ == "__main__":
    unittest.main()