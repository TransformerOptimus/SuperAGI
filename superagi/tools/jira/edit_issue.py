from typing import Type

from superagi.tools.jira.tool import JiraTool, JiraIssueSchema


class EditIssueTool(JiraTool):
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