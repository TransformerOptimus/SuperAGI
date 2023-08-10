# import unittest
# from unittest.mock import patch, MagicMock, ANY
# from superagi.models.agent import Agent
# import os
# from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool, SendEmailAttachmentInput
# import tempfile

# class TestSendEmailAttachmentTool(unittest.TestCase):
#     # Create a new class-level test file
#     testFile = tempfile.NamedTemporaryFile(delete=True)

#     @patch("superagi.models.agent.Agent.get_agent_from_id")
#     @patch("superagi.tools.email.send_email_attachment.SendEmailAttachmentTool.send_email_with_attachment")
#     @patch("superagi.helper.resource_helper.ResourceHelper.get_agent_read_resource_path")
#     @patch("superagi.helper.resource_helper.ResourceHelper.get_root_input_dir")
#     @patch("os.path.exists", return_value=os.path.exists(testFile.name))
#     @patch("superagi.helper.s3_helper.S3Helper.read_binary_from_s3")
#     def test__execute(self, mock_s3_file_read, mock_exists, mock_get_root_input_dir, mock_get_agent_resource_path,
#                       mock_send_email_with_attachment, mock_get_agent_from_id):

#         # Arrange
#         tool = SendEmailAttachmentTool()
#         tool.agent_id = 1
#         mock_get_agent_resource_path.return_value = self.testFile.name
#         mock_get_root_input_dir.return_value = "/root_dir/"
#         mock_send_email_with_attachment.return_value = "Email sent"
#         expected_result = "Email sent"
#         mock_get_agent_from_id.return_value = Agent(id=1, name='Test Agent')
#         tool.agent_execution_id = 1
#         tool.toolkit_config.session = MagicMock()
#         mock_s3_file_read.return_value = b"file contents"

#         # Act
#         result = tool._execute("test@example.com", "test subject", "test body", "test.txt")

#         # Assert
#         self.assertEqual(result, expected_result)
#         mock_send_email_with_attachment.assert_called_once_with("test@example.com", "test subject", "test body", ANY)
#         mock_s3_file_read.assert_called_once_with(self.testFile.name)

# if __name__ == "__main__":
#     unittest.main()
