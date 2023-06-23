from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.github.add_file import GithubAddFileTool
from superagi.tools.github.delete_file import GithubDeleteFileTool
from superagi.tools.github.search_repo import GithubRepoSearchTool


class GitHubToolkit(BaseToolkit, ABC):
    name: str = "GitHub Toolkit"
    description: str = "GitHub Tool Kit contains all github related to tool"

    def get_tools(self) -> List[BaseTool]:
        return [GithubAddFileTool(), GithubDeleteFileTool(), GithubRepoSearchTool()]

    def get_env_keys(self) -> List[str]:
        return [
            "GITHUB_ACCESS_TOKEN",
            "GITHUB_USERNAME",
            # Add more file related config keys here
        ]
