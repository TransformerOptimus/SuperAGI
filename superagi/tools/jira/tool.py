
from jira import JIRA
from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool


class JiraIssueSchema(BaseModel):
    issue_key: str = Field(
        ...,
        description="The key of the Jira issue.",
    )
    fields: dict = Field(
        ...,
        description="The fields to update for the Jira issue.",
    )


class JiraTool(BaseTool):
    """
    Jira tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """

    def build_jira_instance(self) -> dict:
        """
        Build a Jira instance.

        Returns:
            The Jira instance.
        """
        jira_instance_url = self.get_tool_config("JIRA_INSTANCE_URL")
        jira_username = self.get_tool_config("JIRA_USERNAME")
        jira_api_token = self.get_tool_config("JIRA_API_TOKEN")
        jira = JIRA(
            server=jira_instance_url, basic_auth=(jira_username, jira_api_token)
        )
        return jira
