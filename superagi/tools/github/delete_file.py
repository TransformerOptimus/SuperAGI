from typing import Type

from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.helper.github_helper import GithubHelper
from superagi.lib.logger import logger


class GithubDeleteFileSchema(BaseModel):
    # """Input for CopyFileTool."""
    repository_name: str = Field(
        ...,
        description="Repository name in which file hase to be deleted",
    )
    base_branch: str = Field(
        ...,
        description="branch to interact with",
    )
    file_name: str = Field(
        ...,
        description="file name to be deleted in the repository",
    )
    folder_path: str = Field(
        ...,
        description="folder path in which file to be deleted is present",
    )
    commit_message: str = Field(
        ...,
        description="clear description of files that are being deleted",
    )
    repository_owner: str = Field(
        ...,
        description="Owner of the github repository",
    )


class GithubDeleteFileTool(BaseTool):
    """
    Delete File tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Github Delete File"
    args_schema: Type[BaseModel] = GithubDeleteFileSchema
    description: str = "Delete a file or folder inside a particular github repository"

    def _execute(self, repository_name: str, base_branch: str, file_name: str, commit_message: str,
                 repository_owner: str, folder_path=None) -> str:
        """
        Execute the delete file tool.

        Args:
            repository_name : The name of the repository to delete file from.
            base_branch : The branch to interact with.
            file_name : The name of the file to delete.
            commit_message : Clear description of the contents of file.
            repository_owner : Owner of the GitHub repository.
            folder_path : The path of the folder to delete the file from.

        Returns:
            success message mentioning the pull request name for the delete file operation. or error message.
        """

        try:
            github_access_token = self.get_tool_config("GITHUB_ACCESS_TOKEN")
            github_username = self.get_tool_config("GITHUB_USERNAME")
            github_helper = GithubHelper(github_access_token, github_username)
            head_branch = 'new-file'
            headers = {
                "Authorization": f"token {github_access_token}" if github_access_token else None,
                "Content-Type": "application/vnd.github+json"
            }
            if repository_owner != github_username:
                fork_response = github_helper.make_fork(repository_owner, repository_name, base_branch, headers)
            branch_response = github_helper.create_branch(repository_name, base_branch, head_branch, headers)
            logger.info("branch_response", branch_response)
            if branch_response == 201 or branch_response == 422:
                github_helper.sync_branch(github_username, repository_name, base_branch, head_branch, headers)

            file_response = github_helper.delete_file(repository_name, file_name, folder_path, commit_message,
                                                      head_branch, headers)
            pr_response = github_helper.create_pull_request(repository_owner, repository_name, head_branch, base_branch,
                                                            headers)
            if (pr_response == 201 or pr_response == 422) and (file_response == 200):
                return f"Pull request to Delete {file_name} has been created"
            else:
                return "Error while deleting file"
        except Exception as err:
            return f"Error: Unable to delete file {file_name} in {repository_name} repository"
