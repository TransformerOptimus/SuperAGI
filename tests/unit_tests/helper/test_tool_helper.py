import os
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from superagi.helper.tool_helper import (
    parse_github_url,
    load_module_from_file,
    extract_repo_name,
    get_readme_content_from_code_link, download_tool, handle_tools_import, compare_toolkit, compare_configs,
    compare_tools
)


def setup_function():
    os.makedirs('target_folder', exist_ok=True)


# Teardown function to remove the directory
def teardown_function():
    shutil.rmtree('target_folder')


@pytest.fixture
def mock_requests_get(monkeypatch):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code
            self.text = content.decode() if content is not None else None

    def mock_get(url):
        if url == 'https://api.github.com/repos/owner/repo/zipball/main':
            return MockResponse(b'ZIP_CONTENT', 200)
        elif url == 'https://raw.githubusercontent.com/username/repo/main/README.MD':
            return MockResponse(b'README_CONTENT', 200)
        elif url == 'https://raw.githubusercontent.com/username/repo/main/README.md':
            return MockResponse(b'README_CONTENT', 200)
        else:
            return MockResponse(None, 404)

    monkeypatch.setattr('requests.get', mock_get)


def test_parse_github_url():
    github_url = 'https://github.com/owner/repo'
    expected_result = 'owner/repo/main'
    assert parse_github_url(github_url) == expected_result


def test_load_module_from_file(tmp_path):
    current_dir = os.getcwd()
    file_path = Path(current_dir) / 'test_module.py'

    # Corrected code with proper indentation
    file_content = '''
def hello():
    return 'Hello, world!'
'''
    file_path.write_text(file_content)

    module = load_module_from_file(file_path)
    assert module.hello() == 'Hello, world!'

    # Delete the test_module.py file
    file_path.unlink()


def test_get_readme_content_from_code_link(mock_requests_get):
    tool_code_link = 'https://github.com/username/repo'
    expected_result = 'README_CONTENT'
    assert get_readme_content_from_code_link(tool_code_link) == expected_result


def test_extract_repo_name():
    repo_link = 'https://github.com/username/repo'
    expected_result = 'repo'
    assert extract_repo_name(repo_link) == expected_result


@patch('requests.get')
@patch('zipfile.ZipFile')
def test_download_tool(mock_zip, mock_get):
    mock_response = Mock()
    mock_response.content = b'file content'
    mock_get.return_value = mock_response

    # Mock zipfile to return a list of files
    mock_zip.return_value.__enter__.return_value.namelist.return_value = ['owner-repo/somefile.txt']

    download_tool('https://github.com/owner/repo', 'target_folder')

    # Assert that the function made the correct HTTP request
    mock_get.assert_called_once_with('https://api.github.com/repos/owner/repo/zipball/main')

    # Assert zipfile was opened correctly
    mock_zip.assert_called_once_with('target_folder/tool.zip', 'r')


def test_handle_tools_import():
    with patch('superagi.config.config.get_config') as mock_get_config, \
            patch('os.listdir') as mock_listdir, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        mock_get_config.return_value = "superagi/tools"
        mock_listdir.return_value = "test_tool"
        initial_path_length = len(sys.path)
        handle_tools_import()
        assert len(sys.path), initial_path_length + 2

def test_compare_tools():
    tool1 = {"name": "Tool A", "description": "This is Tool A"}
    tool2 = {"name": "Tool A", "description": "This is Tool A"}
    assert not compare_tools(tool1, tool2)

    tool1 = {"name": "Tool A", "description": "This is Tool A"}
    tool2 = {"name": "Tool B", "description": "This is Tool A"}
    assert compare_tools(tool1, tool2)

    tool1 = {"name": "Tool A", "description": "This is Tool A"}
    tool2 = {"name": "Tool A", "description": "This is Tool B"}
    assert compare_tools(tool1, tool2)

def test_compare_configs():
    config1 = {"key": "config_key"}
    config2 = {"key": "config_key"}
    assert not compare_configs(config1, config2)

    config1 = {"key": "config_key_1"}
    config2 = {"key": "config_key_2"}
    assert compare_configs(config1, config2)

def test_compare_toolkit():
    toolkit1 = {
        "description": "Toolkit Description",
        "show_toolkit": True,
        "name": "Toolkit",
        "tool_code_link": "https://example.com/toolkit",
        "tools": [{"name": "Tool A", "description": "This is Tool A"}],
        "configs": [{"key": "config_key"}]
    }
    toolkit2 = {
        "description": "Toolkit Description",
        "show_toolkit": True,
        "name": "Toolkit",
        "tool_code_link": "https://example.com/toolkit",
        "tools": [{"name": "Tool A", "description": "This is Tool A"}],
        "configs": [{"key": "config_key"}]
    }
    assert not compare_toolkit(toolkit1, toolkit2)

    toolkit1 = {
        "description": "Toolkit Description",
        "show_toolkit": True,
        "name": "Toolkit",
        "tool_code_link": "https://example.com/toolkit",
        "tools": [{"name": "Tool A", "description": "This is Tool A"}],
        "configs": [{"key": "config_key"}]
    }
    toolkit2 = {
        "description": "Toolkit Description",
        "show_toolkit": True,
        "name": "Toolkit",
        "tool_code_link": "https://example.com/toolkit",
        "tools": [{"name": "Tool A", "description": "This is Tool B"}],
        "configs": [{"key": "config_key"}]
    }
    assert compare_toolkit(toolkit1, toolkit2)

    toolkit1 = {
        "description": "Toolkit Description",
        "show_toolkit": True,
        "name": "Toolkit",
        "tool_code_link": "https://example.com/toolkit",
        "tools": [{"name": "Tool A", "description": "This is Tool A"}],
        "configs": [{"key": "config_key_1"}]
    }
    toolkit2 = {
        "description": "Toolkit Description",
        "show_toolkit": True,
        "name": "Toolkit",
        "tool_code_link": "https://example.com/toolkit",
        "tools": [{"name": "Tool A", "description": "This is Tool A"}],
        "configs": [{"key": "config_key_2"}]
    }
    assert compare_toolkit(toolkit1, toolkit2)
