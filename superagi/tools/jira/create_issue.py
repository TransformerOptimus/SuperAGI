from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.jira.tool import JiraTool, JiraIssueSchema


class CreateIssueSchema(BaseModel):
    fields: dict = Field(
        ...,
        description='Dictionary of fields to create the Jira issue with. Format: {{"summary": "test issue", "project": "project_id", "description": "test description", "issuetype": {{"name": "Task"}}, "priority": {{"name": "Low"}}}}',
    )


class CreateIssueTool(JiraTool):
    """
    Create Jira Issue tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "CreateJiraIssue"
    description = "Create a new Jira issue."
    args_schema: Type[CreateIssueSchema] = CreateIssueSchema

    def _execute(self, fields: dict):
        """
        Execute the create issue tool.

        Args: fields (dict): Dictionary of fields to create the Jira issue with. Format: {"summary": "test issue",
        "project": "project_id", "description": "test description", "issuetype": {"name": "Task"}, "priority": {
        "name": "Low"}}

        Returns:
            The success message mentioning the key of the created issue.
        """
        jira = self.build_jira_instance()
        new_issue = jira.create_issue(fields=fields)
        return f"Issue '{new_issue.key}' created successfully!"
