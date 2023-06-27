from unittest.mock import patch, MagicMock

from superagi.tools.email.send_email import SendEmailTool


def mock_get_tool_config(key):
    configs = {
        'EMAIL_ADDRESS': 'sender@example.com',
        'EMAIL_PASSWORD': 'password',
        'EMAIL_SIGNATURE': '',
        'EMAIL_DRAFT_MODE': 'False',
        'EMAIL_DRAFT_FOLDER': 'Drafts',
        'EMAIL_IMAP_SERVER': 'imap.example.com',
        'EMAIL_SMTP_HOST': 'host',
        'EMAIL_SMTP_PORT': 'port',
    }
    return configs.get(key)

def mock_get_draft_tool_config(key):
    configs = {
        'EMAIL_ADDRESS': 'sender@example.com',
        'EMAIL_PASSWORD': 'password',
        'EMAIL_SIGNATURE': '',
        'EMAIL_DRAFT_MODE': 'True',
        'EMAIL_DRAFT_FOLDER': 'Drafts',
        'EMAIL_IMAP_SERVER': 'imap.example.com',
        'EMAIL_SMTP_HOST': 'host',
        'EMAIL_SMTP_PORT': 'port',
    }
    return configs.get(key)


@patch('smtplib.SMTP')
@patch('superagi.helper.imap_email.ImapEmail.imap_open')
def test_execute_sends_email(mock_imap_open, mock_smtp):
    # Given
    send_email_tool = SendEmailTool()
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = 'data'

    send_email_tool.toolkit_config.get_tool_config = mock_get_tool_config

    # When
    result = send_email_tool._execute('receiver@example.com', 'test subject', 'test body')

    # Then
    assert result == 'Email was sent to receiver@example.com'
    mock_smtp.assert_called_once_with('host', 'port')


@patch('smtplib.SMTP')
@patch('superagi.helper.imap_email.ImapEmail.imap_open')
def test_execute_sends_email_to_draft(mock_imap_open, mock_smtp):
    send_email_tool = SendEmailTool()
    send_email_tool.toolkit_config.get_tool_config = mock_get_draft_tool_config

    result = send_email_tool._execute('receiver@example.com', 'test subject', 'test body')

    assert result == 'Email went to Drafts'
    mock_imap_open.assert_called_once_with('Drafts', 'sender@example.com', 'password', 'imap.example.com')
    mock_imap_instance = mock_imap_open.return_value
    mock_imap_instance.append.assert_called_once()
    mock_smtp.assert_not_called()