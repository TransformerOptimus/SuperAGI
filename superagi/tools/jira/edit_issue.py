from typing import Type

from pydantic import Field, BaseModel

from superagi.tools.jira.tool import JiraTool, JiraIssueSchema


class EditIssueSchema(BaseModel):
    key: str = Field(
        ...,
        description="Issue key or id in Jira",
    )
    fields: dict = Field(
        ...,
        description='Dictionary of fields to create the Jira issue with. Format: {{"summary": "test issue", "description": "test description", "issuetype": {{"name": "Task"}}, "priority": {{"name": "Low"}}}}',
    )


class EditIssueTool(JiraTool):
    name = "EditJiraIssue"
    description = "Edit a Jira issue."
    args_schema: Type[EditIssueSchema] = EditIssueSchema

    def _execute(self, key: str, fields: dict):
        jira = JiraTool.build_jira_instance()
        issues = jira.search_issues('key=')
        if len(issues) > 0:
            issues[0].update(fields=fields)
            return f"Issue '{issues[0].key}' created successfully!"
        return f"Issue not found!"
