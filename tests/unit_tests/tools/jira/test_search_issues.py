from unittest.mock import Mock, patch

from superagi.tools.jira.search_issues import SearchJiraTool
from unittest.mock import Mock, patch

from superagi.tools.jira.search_issues import SearchJiraTool


@patch("superagi.tools.jira.tool.JiraTool.build_jira_instance")
def test_search_jira_tool(mock_build_jira_instance):
    # Arrange
    mock_jira_instance = Mock()
    mock_issue_1 = Mock()
    mock_issue_1.key = "TEST-1"
    mock_issue_1.fields.summary = "Test issue summary 1"
    mock_issue_1.fields.created = "2023-06-01T10:20:30.400Z"
    mock_issue_1.fields.priority.name = "High"
    mock_issue_1.fields.status.name = "Open"
    mock_issue_1.fields.assignee = None
    mock_issue_1.fields.issuelinks = []
    mock_issues = [mock_issue_1]
    mock_jira_instance.search_issues.return_value = {"issues": mock_issues}
    mock_build_jira_instance.return_value = mock_jira_instance
    tool = SearchJiraTool()
    query = 'summary ~ "test"'

    # Act
    result = tool._execute(query)

    # Assert
    mock_jira_instance.search_issues.assert_called_once_with(query)
    assert "Found 1 issues" in result
    assert f"'key': '{mock_issue_1.key}'" in result
    assert f"'summary': '{mock_issue_1.fields.summary}'" in result
    assert f"'priority': '{mock_issue_1.fields.priority.name}'" in result
    assert f"'status': '{mock_issue_1.fields.status.name}'" in result
    assert "'related_issues': {}" in result
