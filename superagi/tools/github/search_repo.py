from typing import Type, List
from pydantic import BaseModel, Field

from superagi.helper.github_helper import GithubHelper
from superagi.helper.token_counter import TokenCounter
from superagi.tools.base_tool import BaseTool
import os
import json
from superagi.config.config import get_config



class GithubSearchRepoSchema(BaseModel):
    repository_name: str = Field(
        ...,
        description="Repository name in which we have to search",
    )
    repository_owner: str = Field(
        ...,
        description="Owner of the github repository",
    )
    file_name: str = Field(
        ...,
        description="Name of the file we need to fetch from the repository",
    )
    folder_path: str = Field(
        ...,
        description="folder path in which file is present",
    )


class GithubRepoSearchTool(BaseTool):
    name = "GithubRepo Search"
    description = (
        "Search for a file inside a Github repository"
    )
    args_schema: Type[GithubSearchRepoSchema] = GithubSearchRepoSchema
    
    def _execute(self, repository_owner:str, repository_name: str,file_name: str,folder_path=None) -> str:
        github_access_token = get_config("GITHUB_ACCESS_TOKEN")
        github_username = get_config("GITHUB_USERNAME")
        githubrepo_search = GithubHelper(github_access_token,github_username)
        content= githubrepo_search.get_content_in_file(repository_owner,repository_name,file_name,folder_path)

        return content