import pytest
from unittest.mock import MagicMock
import sys
from superagi.helper.tool_helper import (
    parse_github_url,
    download_tool,
    get_classes_in_file,
    load_module_from_file,
    init_tools,
    init_tool_kits,
    process_files,
    get_readme_content_from_code_link,
    register_tool_kits,
    extract_repo_name,
    add_tool_to_json
)

from superagi.models.tool import Tool
from superagi.models.tool_kit import ToolKit
from superagi.tools.base_tool import BaseTool
import json

@pytest.fixture
def mock_requests_get(monkeypatch):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

    def mock_get(url):
        if url == 'https://api.github.com/repos/owner/repo/zipball/main':
            return MockResponse(b'ZIP_CONTENT', 200)
        elif url == 'https://raw.githubusercontent.com/username/repo/main/README.MD':
            return MockResponse(b'README_CONTENT', 200)
        elif url == 'https://raw.githubusercontent.com/username/repo/main/README.md':
            return MockResponse(b'README_CONTENT', 200)
        else:
            return MockResponse(None, 404)

    monkeypatch.setattr('tool.requests.get', mock_get)


def test_parse_github_url():
    github_url = 'https://github.com/owner/repo'
    expected_result = 'owner/repo/main'
    assert parse_github_url(github_url) == expected_result


# def test_download_tool(mock_requests_get, tmp_path):
#     tool_url = 'https://github.com/owner/repo'
#     target_folder = tmp_path
#     download_tool(tool_url, target_folder)
#     assert (target_folder / 'tool.zip').is_file()
#     assert (target_folder / 'file.txt').is_file()


def test_get_classes_in_file(tmp_path):
    file_path = tmp_path / 'test_tool.py'
    file_path.write_text('''
        class Tool1(BaseTool):
            pass

        class Tool2(BaseTool):
            pass

        class NotATool:
            pass
    ''')
    classes = get_classes_in_file(file_path, BaseTool)
    assert len(classes) == 2
    assert {'class_name': 'Tool1'} in classes
    assert {'class_name': 'Tool2'} in classes


# def test_load_module_from_file(tmp_path):
#     file_path = tmp_path / 'test_module.py'
#     file_path.write_text('''
#         def hello():
#             return 'Hello, world!'
#     ''')
#     module = load_module_from_file(file_path)
#     assert module.hello() == 'Hello, world!'


def test_init_tools(tmp_path, monkeypatch):
    session = MagicMock()
    tool_name_to_tool_kit = {
        ('Tool1', 'ToolKit1'): 1,
        ('Tool2', 'ToolKit2'): 2
    }
    folder_dir = tmp_path / 'tools'
    folder_dir.mkdir()
    tool_file = folder_dir / 'tool.py'
    tool_file.write_text('''
        class Tool1(BaseTool):
            name = 'Tool1'

        class Tool2(BaseTool):
            name = 'Tool2'

        class Tool3(BaseTool):
            name = 'Tool3'
    ''')
    sys.path.append(str(folder_dir))
    init_tools(str(tmp_path), session, tool_name_to_tool_kit)
    session.query.assert_called_once_with(Tool)
    session.commit.assert_called_once()


def test_init_tool_kits(tmp_path, monkeypatch):
    session = MagicMock()
    organisation = MagicMock()
    code_link = 'https://github.com/username/repo'
    folder_dir = tmp_path / 'toolkits'
    folder_dir.mkdir()
    toolkit_file = folder_dir / 'toolkit.py'
    toolkit_file.write_text('''
        class ToolKit1(BaseToolKit):
            name = 'ToolKit1'

        class ToolKit2(BaseToolKit):
            name = 'ToolKit2'

        class ToolKit3(BaseToolKit):
            name = 'ToolKit3'
    ''')
    sys.path.append(str(folder_dir))
    tool_name_to_tool_kit = init_tool_kits(code_link, [], str(tmp_path), organisation, session)
    assert tool_name_to_tool_kit == {
        ('Tool1', 'ToolKit1'): 1,
        ('Tool2', 'ToolKit2'): 2
    }
    session.query.assert_called_once_with(ToolKit)
    session.commit.assert_called_once()


def test_process_files(tmp_path, monkeypatch):
    session = MagicMock()
    organisation = MagicMock()
    code_link = 'https://github.com/username/repo'
    folder_dir = tmp_path / 'tools'
    folder_dir.mkdir()
    tool_file = folder_dir / 'tool.py'
    tool_file.write_text('''
        class Tool1(BaseTool):
            name = 'Tool1'

        class Tool2(BaseTool):
            name = 'Tool2'

        class Tool3(BaseTool):
            name = 'Tool3'
    ''')
    toolkit_folder_dir = tmp_path / 'toolkits'
    toolkit_folder_dir.mkdir()
    toolkit_file = toolkit_folder_dir / 'toolkit.py'
    toolkit_file.write_text('''
        class ToolKit1(BaseToolKit):
            name = 'ToolKit1'

        class ToolKit2(BaseToolKit):
            name = 'ToolKit2'

        class ToolKit3(BaseToolKit):
            name = 'ToolKit3'
    ''')
    sys.path.append(str(folder_dir))
    sys.path.append(str(toolkit_folder_dir))
    process_files(str(tmp_path), session, organisation, code_link=code_link)
    session.query.assert_called_with(Tool)
    session.commit.assert_called_once()


def test_get_readme_content_from_code_link(mock_requests_get):
    tool_code_link = 'https://github.com/username/repo'
    expected_result = 'README_CONTENT'
    assert get_readme_content_from_code_link(tool_code_link) == expected_result


def test_register_tool_kits(monkeypatch):
    session = MagicMock()
    organisation = MagicMock()
    folder_path = 'superagi/tools'
    monkeypatch.setattr('tool.get_config', lambda key: folder_path)
    process_files = MagicMock()
    monkeypatch.setattr('tool.process_files', process_files)
    register_tool_kits(session, organisation)
    process_files.assert_called_once_with(folder_path, session, organisation)


def test_extract_repo_name():
    repo_link = 'https://github.com/username/repo'
    expected_result = 'repo'
    assert extract_repo_name(repo_link) == expected_result


def test_add_tool_to_json(tmp_path):
    file_path = tmp_path / 'tools.json'
    file_path.write_text('''
        {
            "tools": {
                "repo1": "https://github.com/username/repo1",
                "repo2": "https://github.com/username/repo2"
            }
        }
    ''')
    repo_link = 'https://github.com/username/repo3'
    add_tool_to_json(repo_link)
    with open(file_path) as file:
        tools_data = json.load(file)
    assert tools_data['tools']['repo1'] == 'https://github.com/username/repo1'
    assert tools_data['tools']['repo2'] == 'https://github.com/username/repo2'
    assert tools_data['tools']['repo3'] == 'https://github.com/username/repo3'

    # Remove the added tool from tools.json
    with open(file_path, 'r') as file:
        tools_data = json.load(file)
    del tools_data['tools']['repo1']
    del tools_data['tools']['repo2']
    del tools_data['tools']['repo3']
    with open(file_path, 'w') as file:
        json.dump(tools_data, file, indent=2)
