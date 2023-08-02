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
        description='Dictionary of fields to create the Jira issue with. Format: {{"summary": "test issue", "project": "project_id", "description": "test description", "issuetype": {{"name": "Task"}}, "priority": {{"name": "Low"}}}}',
    )


class EditIssueTool(JiraTool):
    """
    Edit Jira Issue tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "EditJiraIssue"
    description = "Edit a Jira issue."
    args_schema: Type[EditIssueSchema] = EditIssueSchema

    def _execute(self, key: str, fields: dict):
        """
        Execute the edit issue tool.

        Args:
            key : Issue key or id in Jira
            fields (dict): Dictionary of fields to create the Jira issue with. Format: {"summary": "test issue",
            "project": "project_id", "description": "test description", "issuetype": {"name": "Task"}, "priority": {
            "name": "Low"}}

        Returns:
            The success message mentioning key of the edited issue or Issue not found!
        """
        jira = self.build_jira_instance()
        issues = jira.search_issues('key=')
        if issues:
            issues[0].update(fields=fields)
            return f"Issue '{issues[0].key}' created successfully!"
        return f"Issue not found!"
