import pytest
from unittest.mock import patch, mock_open

from superagi.tools.file.read_file import ReadFileTool


@pytest.fixture
def read_file_tool():
    read_file_tool = ReadFileTool()
    read_file_tool.agent_id = 1  # Set a dummy agent ID for testing.

    yield read_file_tool


def test_read_file_success(read_file_tool):
    # Mock the open function, and make it return a file object that has 'Hello, World!' as its contents.
    mock_file = mock_open(read_data='Hello, World!')
    with patch('builtins.open', mock_file), \
            patch('os.path.exists', return_value=True), \
            patch('os.makedirs', return_value=True), \
            patch('superagi.helper.resource_helper.ResourceHelper.get_root_input_dir',
                  return_value="/input_dir/{agent_id}/"), \
            patch('superagi.helper.resource_helper.ResourceHelper.get_root_output_dir',
                  return_value="/output_dir/{agent_id}/"):
        file_content = read_file_tool._execute('file.txt')

    expected_content = 'Hello, World!\n File file.txt read successfully.'
    assert file_content == expected_content


def test_read_file_file_not_found(read_file_tool):
    with patch('os.path.exists', return_value=False), \
            patch('superagi.helper.resource_helper.ResourceHelper.get_root_input_dir',
                  return_value="/input_dir/{agent_id}/"), \
            patch('superagi.helper.resource_helper.ResourceHelper.get_root_output_dir',
                  return_value="/output_dir/{agent_id}/"):
        with pytest.raises(FileNotFoundError):
            read_file_tool._execute('file.txt')
