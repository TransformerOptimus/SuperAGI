from superagi.tools.email.send_email import SendEmailTool
import pytest

def test_send_to_draft(mocker):

    mock_get_config = mocker.patch('superagi.tools.email.send_email.get_config', autospec=True)
    mock_get_config.side_effect = [
        'test_sender@test.com',  # EMAIL_ADDRESS
        'password',  # EMAIL_PASSWORD
        'Test Signature',  # EMAIL_SIGNATURE
        "Draft",  # EMAIL_DRAFT_MODE_WITH_FOLDER
        'smtp_host',  # EMAIL_SMTP_HOST
        'smtp_port'  # EMAIL_SMTP_PORT
    ]


    # Mocking the ImapEmail call
    mock_imap_email = mocker.patch('superagi.tools.email.send_email.ImapEmail')
    mock_imap_instance = mock_imap_email.return_value.imap_open.return_value

    # Mocking the SMTP call
    mock_smtp = mocker.patch('smtplib.SMTP')
    smtp_instance = mock_smtp.return_value

    # Test the SendEmailTool's execute method
    send_email_tool = SendEmailTool()
    result = send_email_tool._execute('mukunda@contlo.com', 'Test Subject', 'Test Body')

    # Assert the return value
    assert result == 'Email went to Draft'

def test_send_to_mailbox(mocker):
    # Mocking the get_config calls
    mock_get_config = mocker.patch('superagi.tools.email.send_email.get_config')
    mock_get_config.side_effect = [
        'test_sender@test.com',  # EMAIL_ADDRESS
        'password',  # EMAIL_PASSWORD
        'Test Signature',  # EMAIL_SIGNATURE
        "YOUR_DRAFTS_FOLDER",  # EMAIL_DRAFT_MODE_WITH_FOLDER
        'smtp_host',  # EMAIL_SMTP_HOST
        'smtp_port'  # EMAIL_SMTP_PORT
    ]

    # mock_get_config.return_value = 'True'
    # Mocking the ImapEmail call
    mock_imap_email = mocker.patch('superagi.tools.email.send_email.ImapEmail')
    mock_imap_instance = mock_imap_email.return_value.imap_open.return_value

    # Mocking the SMTP call
    mock_smtp = mocker.patch('smtplib.SMTP')
    smtp_instance = mock_smtp.return_value

    # Test the SendEmailTool's execute method
    send_email_tool = SendEmailTool()
    result = send_email_tool._execute('test_receiver@test.com', 'Test Subject', 'Test Body')

    # Assert that the ImapEmail was not called (no draft mode)
    mock_imap_email.assert_not_called()

    # Assert the return value
    assert result == 'Email was sent to test_receiver@test.com'