# from superagi.tools.base_tool import BaseTool


# class JiraTool(BaseTool):
#     def __init__(self):
#         super().__init__("Jira", "Helps to create Jira tickets", self.create_jira_ticket)

#     def execute(self):
#         print("Jira tool")
        
#     def create_jira_ticket(self, name: str):
#         print("hello ramram", name)
#         return
import os
import requests
from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config


class JiraIssueSchema(BaseModel):
    project_key: str = Field(
        ...,
        description="The key of the project in Jira.",
    )
    summary: str = Field(
        ...,
        description="The summary of the issue.",
    )
    description: str = Field(
        ...,
        description="The description of the issue.",
    )
    assignee: str = Field(
        ...,
        description="The username of the assignee for the issue.",
    )

class JiraTool(BaseTool):
    name = "Jira"
    description = (
        "A tool for interacting with the Jira API."
    )
    args_schema: Type[JiraIssueSchema] = JiraIssueSchema

    def execute(self, project_key: str, summary: str, description: str, assignee: str):
        # Retrieve necessary environment variables
        jira_base_url = get_config("JIRA_BASE_URL")
        jira_username = get_config("JIRA_USERNAME")
        jira_token = get_config("JIRA_TOKEN")

        # Prepare the Jira API endpoint URLs
        create_issue_url = f"{jira_base_url}/rest/api/2/issue"
        # assign_user_url = f"{jira_base_url}/rest/api/2/issue/{{issue_key}}/assignee"
        # delete_issue_url = f"{jira_base_url}/rest/api/2/issue/{{issue_key}}"
        # metadata_url = f"{jira_base_url}/rest/api/2/issue/createmeta"

        # Prepare the request headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Prepare the request payload for creating an issue
        issue_payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "assignee": {
                    "name": assignee
                }
            }
        }

        # Create the issue
        response = requests.post(
            create_issue_url,
            headers=headers,
            json=issue_payload,
            auth=(jira_username, jira_token)
        )

        if response.status_code == 201:
            issue_key = response.json()["key"]
            # Assign the user to the issue
            assign_user_payload = {
                "name": assignee
            }
            requests.put(
                assign_user_url.format(issue_key=issue_key),
                headers=headers,
                json=assign_user_payload,
                auth=(jira_username, jira_token)
            )

            # Retrieve metadata about issue creation
            metadata_response = requests.get(
                metadata_url,
                headers=headers,
                auth=(jira_username, jira_token)
            )
            if metadata_response.status_code == 200:
                metadata = metadata_response.json()
                return {
                    "issue_key": issue_key,
                    "metadata": metadata
                }
            else:
                return f"Failed to retrieve metadata. Status code: {metadata_response.status_code}"
        else:
            return f"Failed to create issue. Status code: {response.status_code}"
