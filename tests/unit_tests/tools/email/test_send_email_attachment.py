import unittest
from unittest.mock import patch, Mock, MagicMock, ANY, mock_open
from superagi.models.agent import Agent
import os
from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool, SendEmailAttachmentInput
import tempfile

class TestSendEmailAttachmentTool(unittest.TestCase):
    @patch("superagi.models.agent.Agent.get_agent_from_id")
    @patch("superagi.tools.email.send_email_attachment.SendEmailAttachmentTool.send_email_with_attachment")
    @patch("superagi.helper.resource_helper.ResourceHelper.get_agent_read_resource_path")
    @patch("superagi.helper.resource_helper.ResourceHelper.get_root_input_dir")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("superagi.helper.s3_helper.S3Helper.read_binary_from_s3")
    def test__execute(self, mock_s3_file_read, mock_open, mock_exists, mock_get_root_input_dir, mock_get_agent_resource_path,
                      mock_send_email_with_attachment, mock_get_agent_from_id):
                      
        # Arrange
        tool = SendEmailAttachmentTool()
        tool.agent_id = 1
        mock_exists.return_value = False  # set to False for creating a temp file
        mock_get_agent_resource_path.return_value = "/test/path/test.txt"
        mock_get_root_input_dir.return_value = "/root_dir/"
        mock_send_email_with_attachment.return_value = "Email sent"
        expected_result = "Email sent"
        mock_get_agent_from_id.return_value = Agent(id=1, name='Test Agent')
        tool.agent_execution_id = 1
        tool.toolkit_config.session = MagicMock()
        mock_s3_file_read.return_value = b"file contents"

        # create temporary file if not exists
        if not mock_exists.return_value:  # file does not exist
            with tempfile.NamedTemporaryFile(prefix='test_temp_', delete=False) as f:
                f.write(b'Temporary file content')
                temp_file_name = f.name
                
        mock_open.side_effect = [mock_open(read_data='Temporary file content').return_value]

        # Act
        result = tool._execute("test@example.com", "test subject", "test body", "test.txt")

        # Assert
        self.assertEqual(result, expected_result)
        mock_send_email_with_attachment.assert_called_once_with("test@example.com", "test subject", "test body", ANY)
        mock_s3_file_read.assert_called_once_with("/test/path/test.txt")
        os.remove(temp_file_name)  # clean up temp file

if __name__ == "__main__":
    unittest.main()
