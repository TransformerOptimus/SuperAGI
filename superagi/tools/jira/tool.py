import os

import requests
from typing import List, Type
from pydantic import BaseModel, Field

from superagi.config.config import get_config
from superagi.tools.base_tool import BaseTool
from jira import JIRA

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
    jira_base_url = "https://your-jira-instance.com/rest/api/2"

    @classmethod
    def build_jira_instance(self) -> dict:
        jira_instance_url = get_config("JIRA_INSTANCE_URL")
        jira_username = get_config("JIRA_USERNAME")
        jira_api_token = get_config("JIRA_API_TOKEN")
        jira = JIRA(
            server=jira_instance_url,
            username=jira_username,
            password=jira_api_token,
            cloud=True,
        )
        return jira
