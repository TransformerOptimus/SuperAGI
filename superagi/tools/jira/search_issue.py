from typing import Type

from superagi.tools.jira.tool import JiraTool, JiraIssueSchema


class SearchIssueTool(JiraTool):
    name = "EditIssue"
    description = "Edit an existing Jira issue."
    args_schema: Type[JiraIssueSchema] = JiraIssueSchema

    def execute(self, issue_key: str, fields: dict):
        url = f"{self.jira_base_url}/issue/{issue_key}"
        issue_data = {
            "fields": fields
        }
        response = self.make_request("PUT", url, json=issue_data)
        return f"Issue '{issue_key}' updated successfully!"

    def search(self, query: str) -> str:
        jira = JiraTool.build_jira_instance()
        issues = jira.jql(query)
        parsed_issues = self.parse_issues(issues)
        parsed_issues_str = (
                "Found " + str(len(parsed_issues)) + " issues:\n" + str(parsed_issues)
        )
        return parsed_issues_str
