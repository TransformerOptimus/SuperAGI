from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.github_helper import GithubHelper
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool


class GithubFetchPullRequestSchema(BaseModel):
    repository_name: str = Field(
        ...,
        description="Repository name in which file hase to be added",
    )
    repository_owner: str = Field(
        ...,
        description="Owner of the github repository",
    )
    time_in_seconds: int = Field(
        ...,
        description="Gets pull requests from last `time_in_seconds` seconds",
    )


class GithubFetchPullRequest(BaseTool):
    """
    Fetch pull request tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        agent_id: The agent id.
        agent_execution_id: The agent execution id.
    """
    llm: Optional[BaseLlm] = None
    name: str = "Github Fetch Pull Requests"
    args_schema: Type[BaseModel] = GithubFetchPullRequestSchema
    description: str = "Fetch pull requests from github"
    agent_id: int = None
    agent_execution_id: int = None

    def _execute(self, repository_name: str, repository_owner: str, time_in_seconds: int = 86400) -> str:
        """
        Execute the add file tool.

        Args:
            repository_name: The name of the repository to add file to.
            repository_owner: Owner of the GitHub repository.
            time_in_seconds: Gets pull requests from last `time_in_seconds` seconds

        Returns:
            List of all pull request ids
        """
        try:
            github_access_token = self.get_tool_config("GITHUB_ACCESS_TOKEN")
            github_username = self.get_tool_config("GITHUB_USERNAME")
            github_helper = GithubHelper(github_access_token, github_username)

            pull_request_urls = github_helper.get_pull_requests_created_in_last_x_seconds(repository_owner,
                                                                                          repository_name,
                                                                                          time_in_seconds)

            return "Pull requests: " + str(pull_request_urls)
        except Exception as err:
            return f"Error: Unable to fetch pull requests {err}"
