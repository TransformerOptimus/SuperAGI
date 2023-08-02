from unittest.mock import MagicMock, patch

from superagi.tools.github.delete_file import GithubDeleteFileTool, GithubDeleteFileSchema


def test_github_delete_file_tool():
    # Test case: Successfully delete a file and create a pull request
    with patch("superagi.tools.github.delete_file.GithubHelper") as mock_github_helper:
        mock_github_helper.return_value.make_fork.return_value = 201
        mock_github_helper.return_value.create_branch.return_value = 201
        mock_github_helper.return_value.sync_branch.return_value = None
        mock_github_helper.return_value.delete_file.return_value = 200
        mock_github_helper.return_value.create_pull_request.return_value = 201

        tool = GithubDeleteFileTool()
        tool.toolkit_config.get_tool_config = MagicMock(side_effect=["GITHUB_ACCESS_TOKEN", "GITHUB_USERNAME"])

        args = GithubDeleteFileSchema(
            repository_name="test_repo",
            base_branch="main",
            file_name="test_file.txt",
            folder_path="test_folder",
            commit_message="Delete test_file.txt",
            repository_owner="test_owner"
        )

        result = tool._execute("test_repo", "main", "test_file.txt", "Delete test_file.txt", "test_owner")
        assert result == "Pull request to Delete test_file.txt has been created"

    # Test case: Error while deleting file
    with patch("superagi.tools.github.delete_file.GithubHelper") as mock_github_helper:
        mock_github_helper.return_value.make_fork.return_value = 201
        mock_github_helper.return_value.create_branch.return_value = 201
        mock_github_helper.return_value.sync_branch.return_value = None
        mock_github_helper.return_value.delete_file.return_value = 400
        mock_github_helper.return_value.create_pull_request.return_value = 201

        tool = GithubDeleteFileTool()
        tool.toolkit_config.get_tool_config = MagicMock(side_effect=["GITHUB_ACCESS_TOKEN", "GITHUB_USERNAME"])

        result = tool._execute("test_repo", "main", "test_file.txt", "Delete test_file.txt", "test_owner")
        assert result == "Error while deleting file"