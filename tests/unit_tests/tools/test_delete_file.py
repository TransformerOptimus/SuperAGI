from unittest.mock import patch

import pytest

from superagi.tools.file.delete_file import DeleteFileTool


@pytest.fixture
def delete_file_tool():
    with patch('superagi.tools.file.delete_file.os.remove') as remove_mock:
        remove_mock.return_value = None  # The mock doesn't need to return anything; we just need it not to actually delete files.

        delete_file_tool = DeleteFileTool()
        delete_file_tool.agent_id = 1  # Set a dummy agent ID for testing.

        yield delete_file_tool


def test_delete_existing_file(delete_file_tool):
    with patch('superagi.tools.file.delete_file.os.path.isfile', return_value=True):
        result = delete_file_tool._execute('existing_file.txt')

    assert result == 'File deleted successfully.'
