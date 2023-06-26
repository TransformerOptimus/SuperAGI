import pytest
from unittest.mock import Mock, patch
from superagi.tools.jira.create_issue import CreateIssueTool

CreateIssueTool
@patch("superagi.tools.jira.create_issue.JiraTool.build_jira_instance")
def test_create_issue_tool(mock_build_jira_instance):
    # Arrange
    mock_jira_instance = Mock()
    mock_new_issue = Mock()
    mock_new_issue.key = "TEST-1"
    mock_jira_instance.create_issue.return_value = mock_new_issue
    mock_build_jira_instance.return_value = mock_jira_instance
    tool = CreateIssueTool()
    fields = {
        "summary": "test issue",
        "project": "project_id",
        "description": "test description",
        "issuetype": {"name": "Task"},
        "priority": {"name": "Low"},
    }

    # Act
    result = tool._execute(fields)

    # Assert
    mock_jira_instance.create_issue.assert_called_once_with(fields=fields)
    assert result == f"Issue '{mock_new_issue.key}' created successfully!"