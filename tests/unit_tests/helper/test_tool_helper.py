import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from superagi.helper.tool_helper import (
    parse_github_url,
    load_module_from_file,
    extract_repo_name,
    add_tool_to_json, get_readme_content_from_code_link, download_tool
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
