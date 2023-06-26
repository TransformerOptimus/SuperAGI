from unittest.mock import patch, Mock

from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool


def test_send_email_attachment():
    # Arrange
    with patch('superagi.tools.email.send_email_attachment.smtplib.SMTP') as mock_smtp:
        with patch('superagi.tools.email.send_email_attachment.ImapEmail') as mock_imap_email:
            with patch('superagi.tools.email.send_email_attachment.open', mock=Mock(), create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = b"some file content"
                mock_imap_email_instance = mock_imap_email.return_value
                mock_smtp_instance = mock_smtp.return_value
                tool = SendEmailAttachmentTool()
                tool.toolkit_config.get_tool_config = Mock()
                tool.toolkit_config.get_tool_config.return_value = 'dummy_value'
                mock_smtp_instance.send_message = Mock()
                to = 'test@example.com'
                subject = 'test_subject'
                body = 'test_body'
                filename = 'test_file.txt'

                # Act
                result = tool._execute(to, subject, body, filename)

                # mock_smtp_instance.send_message.assert_called_once()
                assert result == f"Email was sent to {to}"
                assert 'rb' in mock_open.call_args[0]
                assert filename in mock_open.call_args[0][0]
