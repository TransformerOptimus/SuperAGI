import string
import re
import base64

import requests
import os
from typing import Type

from pydantic import BaseModel, Field
from superagi.config.config import get_config

from superagi.tools.base_tool import BaseTool

from superagi.helper.github_helper import GithubHelper


class GithubAddFileSchema(BaseModel):
    # """Input for CopyFileTool."""
    repository_name: str = Field(
        ...,
        description="Repository name in which file hase to be added",
    )
    base_branch: str = Field(
        ...,
        description="branch to interact with",
    )
    file_name: str = Field(
        ...,
        description="file name to be added to repository",
    )
    folder_path: str = Field(
        ...,
        description="folder path for the file to be stored",
    )
    body: str = Field(
        ...,
        description="content to be stored",
    )
    commit_message: str = Field(
        ...,
        description="clear description of the contents of file",
    )
    repository_owner: str = Field(
        ...,
        description="Owner of the github repository",
    )


class GithubAddFileTool(BaseTool):
    """
    Add File tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Github Add File"
    args_schema: Type[BaseModel] = GithubAddFileSchema
    description: str = "Add a file or folder to a particular github repository"

    def _execute(self, repository_name: str, base_branch: str, body: str, commit_message: str, repository_owner: str,
                 file_name='.gitkeep', folder_path=None) -> str:
        """
        Execute the add file tool.

        Args:
            repository_name : The name of the repository to add file to.
            base_branch : The branch to interact with.
            body : The content to be stored.
            commit_message : Clear description of the contents of file.
            repository_owner : Owner of the GitHub repository.
            file_name : The name of the file to add.
            folder_path : The path of the folder to add the file to.

        Returns:
            Pull request to add file/folder has been created. or error message.
        """
        try:
            github_access_token = get_config("GITHUB_ACCESS_TOKEN")
            github_username = get_config("GITHUB_USERNAME")
            github_helper = GithubHelper(github_access_token, github_username)
            head_branch = 'new-file'
            headers = {
                "Authorization": f"token {github_access_token}" if github_access_token else None,
                "Content-Type": "application/vnd.github+json"
            }
            if repository_owner != github_username:
                fork_response = github_helper.make_fork(repository_owner, repository_name, base_branch, headers)

            branch_response = github_helper.create_branch(repository_name, base_branch, head_branch, headers)
            file_response = github_helper.add_file(repository_owner, repository_name, file_name, folder_path,
                                                   head_branch, base_branch, headers, body, commit_message)
            pr_response = github_helper.create_pull_request(repository_owner, repository_name, head_branch, base_branch,
                                                            headers)
            if (pr_response == 201 or pr_response == 422) and (file_response == 201 or file_response == 422):
                return "Pull request to add file/folder has been created"
            else:
                return "Error while adding file."
        except Exception as err:
            return f"Error: Unable to add file/folder to repository {err}"
