import pytest
from unittest.mock import MagicMock, patch

from superagi.helper.github_helper import GithubHelper
from superagi.tools.github.add_file import GithubAddFileTool, GithubAddFileSchema


def test_github_add_file_schema():
    schema = GithubAddFileSchema(
        repository_name="test_repo",
        base_branch="main",
        file_name="test_file",
        folder_path="test_folder",
        commit_message="test_commit",
        repository_owner="test_owner"
    )

    assert schema.repository_name == "test_repo"
    assert schema.base_branch == "main"
    assert schema.file_name == "test_file"
    assert schema.folder_path == "test_folder"
    assert schema.commit_message == "test_commit"
    assert schema.repository_owner == "test_owner"


@pytest.fixture
def github_add_file_tool():
    return GithubAddFileTool()


@patch.object(GithubHelper, "make_fork")
@patch.object(GithubHelper, "create_branch")
@patch.object(GithubHelper, "add_file")
@patch.object(GithubHelper, "create_pull_request")
def test_github_add_file_tool_execute(mock_make_fork, mock_create_branch, mock_add_file, mock_create_pull_request, github_add_file_tool):
    github_add_file_tool.toolkit_config.get_tool_config = MagicMock(side_effect=["test_token", "test_username"])

    mock_make_fork.return_value = 201
    mock_create_branch.return_value = 201
    mock_add_file.return_value = 201
    mock_create_pull_request.return_value = 201

    response = github_add_file_tool._execute(
        repository_name="test_repo",
        base_branch="main",
        commit_message="test_commit",
        repository_owner="test_owner",
        file_name="test_file",
        folder_path="test_folder"
    )

    assert response == "Pull request to add file/folder has been created"

    mock_make_fork.return_value = 422
    mock_create_branch.return_value = 422
    mock_add_file.return_value = 422
    mock_create_pull_request.return_value = 422

    response = github_add_file_tool._execute(
        repository_name="test_repo",
        base_branch="main",
        commit_message="test_commit",
        repository_owner="test_owner",
        file_name="test_file",
        folder_path="test_folder"
    )

    assert response == "Error: Unable to add file/folder to repository "
