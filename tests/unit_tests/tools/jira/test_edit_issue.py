import pytest
from unittest.mock import Mock, patch

from superagi.tools.jira.edit_issue import EditIssueTool


@patch("superagi.tools.jira.edit_issue.JiraTool.build_jira_instance")
def test_edit_issue_tool(mock_build_jira_instance):
    # Arrange
    mock_jira_instance = Mock()
    mock_issue = Mock()
    mock_issue.key = "TEST-1"
    mock_jira_instance.search_issues.return_value = [mock_issue]
    mock_build_jira_instance.return_value = mock_jira_instance
    tool = EditIssueTool()
    key = "TEST-1"
    fields = {
        "summary": "test issue",
        "project": "project_id",
        "description": "test description",
        "issuetype": {"name": "Task"},
        "priority": {"name": "Low"},
    }

    # Act
    result = tool._execute(key, fields)

    # Assert
    mock_jira_instance.search_issues.assert_called_once_with("key=")
    mock_issue.update.assert_called_once_with(fields=fields)
    assert result == f"Issue '{mock_issue.key}' created successfully!"
