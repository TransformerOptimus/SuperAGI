from unittest.mock import MagicMock, patch

import pytest

from superagi.tools.file.list_files import ListFileTool


@pytest.fixture
def list_file_tool():
    list_file_tool = ListFileTool()
    list_file_tool.agent_id = 1  # Set a dummy agent ID for testing.
    # list_file_tool = "test_agent"
    mock_session = MagicMock(name="session")
    list_file_tool.toolkit_config.session = mock_session

    yield list_file_tool

def test_list_files(list_file_tool):
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('/path/to', ('subdir',), ('file1.txt', '.file2.txt')),
            ('/path/to/subdir', (), ('file3.txt', 'file4.txt'))
        ]

        files = list_file_tool.list_files('/path/to')

    assert files == ['file1.txt', 'file3.txt', 'file4.txt']

def test_execute(list_file_tool):
    mock_get_formatted_agent_level_path = MagicMock(return_value="SuperAGI/workspace/input/{agent_id}/")

    with patch.object(ListFileTool, 'list_files', return_value=['file1.txt', 'file2.txt']), \
         patch('superagi.helper.resource_helper.ResourceHelper.get_formatted_agent_level_path', new=mock_get_formatted_agent_level_path):

        files = list_file_tool._execute()

    assert files == ['file1.txt', 'file2.txt']