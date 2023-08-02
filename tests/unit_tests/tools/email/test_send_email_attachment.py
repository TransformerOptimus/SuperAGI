import unittest
from unittest.mock import patch, Mock, MagicMock
from superagi.models.agent import Agent
import os
from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool, SendEmailAttachmentInput

class TestSendEmailAttachmentTool(unittest.TestCase):
    @patch("superagi.models.agent.Agent.get_agent_from_id")
    @patch("superagi.tools.email.send_email_attachment.SendEmailAttachmentTool.send_email_with_attachment")
    @patch("superagi.helper.resource_helper.ResourceHelper.get_agent_read_resource_path")
    @patch("superagi.helper.resource_helper.ResourceHelper.get_root_input_dir")
    @patch("os.path.exists")
    def test__execute(self, mock_exists, mock_get_root_input_dir, mock_get_agent_resource_path,
                      mock_send_email_with_attachment, mock_get_agent_from_id):
        # Arrange
        tool = SendEmailAttachmentTool()
        tool.agent_id = 1
        mock_exists.return_value = True
        mock_get_agent_resource_path.return_value = "/test/path/test.txt"
        mock_get_root_input_dir.return_value = "/root_dir/"
        mock_send_email_with_attachment.return_value = "Email sent"
        expected_result = "Email sent"
        mock_get_agent_from_id.return_value = Agent(id=1, name='Test Agent')
        tool.agent_execution_id = 1
        tool.toolkit_config.session = MagicMock()

        # Act
        result = tool._execute("test@example.com", "test subject", "test body", "test.txt")

        # Assert
        self.assertEqual(result, expected_result)
        mock_send_email_with_attachment.assert_called_once_with("test@example.com", "test subject", "test body", "/test/path/test.txt", "test.txt")

if __name__ == "__main__":
    unittest.main()