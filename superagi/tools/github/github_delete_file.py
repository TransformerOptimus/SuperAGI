
import requests
import os
from typing import Type

from pydantic import BaseModel, Field
from superagi.config.config import get_config

from superagi.tools.base_tool import BaseTool


from superagi.helper.github_search import GithubHelper

class GithubDeleteFileSchema(BaseModel):
    # Input for CopyFileTool
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
    name: str = "Github Delete File"
    args_schema: Type[BaseModel] = GithubDeleteFileSchema
    description: str = "Delete a file or folder inside a particular github repository"

    def _execute(self, repository_name: str,base_branch: str,file_name: str,commit_message: str,repository_owner:str,folder_path=None)->str:

        try:
            github_access_token = get_config("GITHUB_ACCESS_TOKEN")
            github_username = get_config("GITHUB_USERNAME")
            github_helper=GithubHelper(github_access_token,github_username)

            file_path=f'{folder_path}'
            if folder_path:
                file_path+='/'
            file_path+=file_name
            head_branch = 'new-file' 
            headers={
                "Authorization": f"token {github_access_token}" if github_access_token else None,
                "Content-Type": "application/vnd.github+json"
            }  

            if(repository_owner!=github_username):
                fork_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/forks'

                # Send the POST request to create the fork
                fork_response = requests.post(fork_url, headers=headers)

                if fork_response.status_code == 202:
                    print('Fork created successfully.')
                    # github_helper.sync_branch(repository_owner,repository_name,base_branch,head_branch)
                    github_helper.sync_branch(repository_owner,repository_name,base_branch,base_branch)
                else:
                    print('Failed to create the fork:', fork_response.json()['message'])  

            # Create a new branch for the changes

            branch_url = f'https://api.github.com/repos/{github_username}/{repository_name}/git/refs'
            # print('base_branch',base_branch)
            branch_params = {
                'ref': f'refs/heads/{head_branch}',
                'sha': requests.get(f'https://api.github.com/repos/{github_username}/{repository_name}/git/refs/heads/{base_branch}',headers=headers).json()['object']['sha']
            }
            branch_response = requests.post(branch_url, json=branch_params, headers=headers)
            # print('branch_response.status_code',branch_response.status_code)
            if branch_response.status_code == 201:
                print('Branch created successfully.')
                github_helper.sync_branch(github_username,repository_name,base_branch,head_branch)
            elif branch_response.status_code == 422:
                print('Branch new-file already exists, making commits to new-file branch')
                github_helper.sync_branch(github_username,repository_name,base_branch,head_branch)
            else:
                print('Failed to create branch:', branch_response.json()['message'])

            
            # Delete the file content
            file_url = f'https://api.github.com/repos/{github_username}/{repository_name}/contents/{file_path}'
            file_params = {
                'message': commit_message,
                'sha': github_helper.get_sha(github_username,repository_name,file_name,folder_path),
                'branch':head_branch
            }
            file_response = requests.delete(file_url, json=file_params, headers=headers)
            # print(file_response)
            if file_response.status_code == 200:
                print('File or folder delete successfully.')
            else:
                print('Failed to Delete file or folder:', file_response.json())


            # Create a pull request
            pull_request_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/pulls'
            pull_request_params = {
                'title': f'Pull request by {github_username}',
                'body': 'Please review and merge this change.',
                'head': f'{github_username}:{head_branch}',  # required for cross repository only
                'head_repo': repository_name,#required for cross repository only
                'base': base_branch
            }
            pr_response = requests.post(pull_request_url, json=pull_request_params, headers=headers)

            if pr_response.status_code == 201:
                print('Pull request created successfully.')
            elif pr_response.status_code == 422:
                print('Added changes to already existing pull request')
            else:
                print('Failed to create pull request:', pr_response.json()['message'])

            # print("pr_response.status_code: ",pr_response.status_code)
            # print("file_response.status_code: ",file_response.status_code)

            if((pr_response.status_code==201 or pr_response.status_code==422) and file_response.status_code==200):
                return f"Pull request to Delete {file_path} has been created"
            else:
                return "Unable to execute the task"  
            
        except Exception as err:
            # print(err)
            return f"Error: Unable to delete the file"


