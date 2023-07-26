import os
import shutil
import tempfile

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from superagi.tool_manager import parse_github_url, download_tool, load_tools_config, download_and_extract_tools

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
    mock_download_tool.assert_any_call('url1', os.path.join('superagi', 'tools', 'tool1'))
    mock_download_tool.assert_any_call('url2', os.path.join('superagi', 'tools', 'tool2'))
