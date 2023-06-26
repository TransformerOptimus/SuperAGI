from unittest.mock import MagicMock, patch

import pytest

from superagi.tools.github.search_repo import GithubRepoSearchTool, GithubSearchRepoSchema


def test_github_search_repo_schema():
    schema = GithubSearchRepoSchema(
        repository_name="test-repo",
        repository_owner="test-owner",
        file_name="test-file",
        folder_path="test-path",
    )

    assert schema.repository_name == "test-repo"
    assert schema.repository_owner == "test-owner"
    assert schema.file_name == "test-file"
    assert schema.folder_path == "test-path"


@pytest.fixture
def github_repo_search_tool():
    return GithubRepoSearchTool()


@patch("superagi.tools.github.search_repo.GithubHelper")
def test_execute(github_helper_mock, github_repo_search_tool):
    github_helper_instance = github_helper_mock.return_value
    github_helper_instance.get_content_in_file.return_value = "test-content"

    github_repo_search_tool.toolkit_config.get_tool_config = MagicMock(side_effect=["test-token", "test-username"])
    result = github_repo_search_tool._execute(
        repository_owner="test-owner",
        repository_name="test-repo",
        file_name="test-file",
        folder_path="test-path",
    )

    github_helper_mock.assert_called_once_with("test-token", "test-username")
    github_helper_instance.get_content_in_file.assert_called_once_with(
        "test-owner", "test-repo", "test-file", "test-path"
    )
    assert result == "test-content"
