from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.github.add_file import GithubAddFileTool
from superagi.tools.github.delete_file import GithubDeleteFileTool
from superagi.tools.github.search_repo import GithubRepoSearchTool
from superagi.types.key_type import ToolConfigKeyType


class GitHubToolkit(BaseToolkit, ABC):
    name: str = "GitHub Toolkit"
    description: str = "GitHub Tool Kit contains all github related to tool"

    def get_tools(self) -> List[BaseTool]:
        return [GithubAddFileTool(), GithubDeleteFileTool(), GithubRepoSearchTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="GITHUB_ACCESS_TOKEN", key_type=ToolConfigKeyType.STRING, is_required= True, is_secret = True),
            ToolConfiguration(key="GITHUB_USERNAME", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=False)
        ]


