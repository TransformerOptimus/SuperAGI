import pytest
from unittest.mock import patch, Mock
from pydantic import ValidationError

from superagi.tools.github.fetch_pull_request import GithubFetchPullRequest, GithubFetchPullRequestSchema


@pytest.fixture
def mock_github_helper():
    with patch('superagi.tools.github.fetch_pull_request.GithubHelper') as MockGithubHelper:
        yield MockGithubHelper


@pytest.fixture
def tool(mock_github_helper):
    tool = GithubFetchPullRequest()
    tool.toolkit_config = Mock()
    tool.toolkit_config.side_effect = ['dummy_token', 'dummy_username']
    mock_github_helper_instance = mock_github_helper.return_value
    mock_github_helper_instance.get_pull_requests_created_in_last_x_seconds.return_value = ['url1', 'url2']
    return tool


def test_execute(tool, mock_github_helper):
    mock_github_helper_instance = mock_github_helper.return_value

    # Execute the method
    result = tool._execute('repo_name', 'repo_owner', 86400)

    # Verify results
    assert result == "Pull requests: ['url1', 'url2']"
    mock_github_helper_instance.get_pull_requests_created_in_last_x_seconds.assert_called_once_with('repo_owner',
                                                                                                    'repo_name', 86400)


def test_schema_validation():
    # Valid data
    valid_data = {'repository_name': 'repo', 'repository_owner': 'owner', 'time_in_seconds': 86400}
    GithubFetchPullRequestSchema(**valid_data)

    # Invalid data
    invalid_data = {'repository_name': 'repo', 'repository_owner': 'owner', 'time_in_seconds': 'string'}
    with pytest.raises(ValidationError):
        GithubFetchPullRequestSchema(**invalid_data)


def test_execute_error(mock_github_helper):
    tool = GithubFetchPullRequest()
    tool.toolkit_config = Mock()
    tool.toolkit_config.side_effect = ['dummy_token', 'dummy_username']
    mock_github_helper_instance = mock_github_helper.return_value
    mock_github_helper_instance.get_pull_requests_created_in_last_x_seconds.side_effect = Exception('An error occurred')

    # Execute the method
    result = tool._execute('repo_name', 'repo_owner', 86400)

    # Verify results
    assert result == 'Error: Unable to fetch pull requests An error occurred'
