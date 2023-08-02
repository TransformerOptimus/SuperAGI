import json
import os
import shutil
import tempfile
from unittest.mock import Mock, patch

import pytest

from superagi.tool_manager import parse_github_url, download_tool, load_tools_config, download_and_extract_tools, \
    update_tools_json


@pytest.fixture
def tools_json_path():
    # Create a temporary directory and return the path to the tools.json file
    with tempfile.TemporaryDirectory() as temp_dir:
        yield os.path.join(temp_dir, "tools.json")


def test_parse_github_url():
    url = 'https://github.com/owner/repo'
    assert parse_github_url(url) == 'owner/repo/main'


def setup_function():
    os.makedirs('target_folder', exist_ok=True)


# Teardown function to remove the directory
def teardown_function():
    shutil.rmtree('target_folder')


@patch('requests.get')
@patch('zipfile.ZipFile')
def test_download_tool(mock_zip, mock_get):
    mock_response = Mock()
    mock_response.content = b'file content'
    mock_get.return_value = mock_response
    mock_zip.return_value.__enter__.return_value.namelist.return_value = ['owner-repo/somefile.txt']

    download_tool('https://github.com/owner/repo', 'target_folder')

    mock_get.assert_called_once_with('https://api.github.com/repos/owner/repo/zipball/main')
    mock_zip.assert_called_once_with('target_folder/tool.zip', 'r')


@patch('json.load')
def test_load_tools_config(mock_json_load):
    mock_json_load.return_value = {"tools": {"tool1": "url1", "tool2": "url2"}}

    config = load_tools_config()
    assert config == {"tool1": "url1", "tool2": "url2"}


@patch('superagi.tool_manager.download_tool')
@patch('superagi.tool_manager.load_tools_config')
def test_download_and_extract_tools(mock_load_tools_config, mock_download_tool):
    mock_load_tools_config.return_value = {"tool1": "url1", "tool2": "url2"}
    download_and_extract_tools()

    mock_load_tools_config.assert_called_once()
    mock_download_tool.assert_any_call('url1', os.path.join('superagi', 'tools', 'external_tools', 'tool1'))
    mock_download_tool.assert_any_call('url2', os.path.join('superagi', 'tools', 'external_tools', 'tool2'))


def test_update_tools_json(tools_json_path):
    # Create an initial tools.json file with some data
    initial_data = {
        "tools": {
            "tool1": "link1",
            "tool2": "link2"
        }
    }
    with open(tools_json_path, "w") as file:
        json.dump(initial_data, file)

    # Define the folder links to be updated
    folder_links = {
        "tool3": "link3",
        "tool4": "link4"
    }

    # Call the function to update the tools.json file
    update_tools_json(tools_json_path, folder_links)

    # Read the updated tools.json file
    with open(tools_json_path, "r") as file:
        updated_data = json.load(file)

    # Assert that the data was updated correctly
    expected_data = {
        "tools": {
            "tool1": "link1",
            "tool2": "link2",
            "tool3": "link3",
            "tool4": "link4"
        }
    }
    assert updated_data == expected_data
