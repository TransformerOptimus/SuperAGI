from unittest.mock import patch, Mock

from superagi.tools.email.read_email import ReadEmailTool


@patch('superagi.tools.email.read_email.ImapEmail')
@patch('superagi.tools.email.read_email.ReadEmail')
def test_execute(mock_read_email, mock_imap_email):
    # Configure the mock objects
    mock_conn = Mock()
    mock_conn.select.return_value = ('OK', ['10'])  # assume 10 messages in INBOX
    mock_conn.fetch.return_value = ('OK', [(b'1 (RFC822 {337}', b'Some email content')])
    mock_imap_email.return_value.imap_open.return_value = mock_conn
    mock_read_email.return_value.obtain_header.return_value = ('From', 'To', 'Date', 'Subject')
    mock_read_email.return_value.clean_email_body.return_value = 'Cleaned email body'

    # Set up ReadEmailTool object
    tool = ReadEmailTool()
    tool.toolkit_config.get_tool_config = Mock()
    tool.toolkit_config.get_tool_config.return_value = 'dummy_value'

    # Call the function
    result = tool._execute()

    # Check the results
    assert len(result) == 5  # check that one email was processed
    assert result[0]['From'] == 'From'
    assert result[0]['To'] == 'To'
    assert result[0]['Date'] == 'Date'
    assert result[0]['Subject'] == 'Subject'
    assert result[0]['Message Body'] == 'Cleaned email body'
