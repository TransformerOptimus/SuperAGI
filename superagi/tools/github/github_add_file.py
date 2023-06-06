import string
import re
import base64

import requests
import os
from typing import Type

from pydantic import BaseModel, Field
from superagi.config.config import get_config


from superagi.tools.base_tool import BaseTool


import tweepy

from superagi.helper.github_search import GithubHelper


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
    name: str = "Github Add File"
    args_schema: Type[BaseModel] = GithubAddFileSchema
    description: str = "Add a file or folder to a particular github repository"
    

    def _execute(self, repository_name: str,base_branch: str,body: str,commit_message: str,repository_owner:str,file_name= '.gitkeep',folder_path=None)->str:

        try:
            github_access_token = get_config("GITHUB_ACCESS_TOKEN")
            github_username = get_config("GITHUB_USERNAME")
            githubrepo_search = GithubHelper(github_access_token,github_username)
            
            file_path=f'{folder_path}'
            if folder_path:
                file_path+='/'
            file_path+=file_name 

            
            head_branch = 'new-file' 
            headers={
                "Authorization": f"token {github_access_token}" if github_access_token else None,
                "Content-Type": "application/vnd.github+json"
            }  

            if(githubrepo_search.get_repository_collaborators(repository_owner,repository_name,github_username)==False):
                fork_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/forks'

                # Send the POST request to create the fork
                fork_response = requests.post(fork_url, headers=headers)

                if fork_response.status_code == 202:
                    print('Fork created successfully.')
                else:
                    print('Failed to create the fork:', fork_response.json()['message'])

            # Create a new branch for the changes

            branch_url = f'https://api.github.com/repos/{github_username}/{repository_name}/git/refs'
            branch_params = {
                'ref': f'refs/heads/{head_branch}',
                'sha': requests.get(f'https://api.github.com/repos/{github_username}/{repository_name}/git/refs/heads/{base_branch}',headers=headers).json()['object']['sha']
            }
            branch_response = requests.post(branch_url, json=branch_params, headers=headers)
            # print(branch_response.status_code)
            if branch_response.status_code == 201:
                print('Branch created successfully.')
            elif branch_response.status_code == 422:
                print('Branch new-file already exists, making commits to new-file branch')
            else:
                print('Failed to create branch:', branch_response.json()['message'])


            # Upload the file content
            body_bytes = body.encode("ascii")
            base64_bytes = base64.b64encode(body_bytes)
            file_content = base64_bytes.decode("ascii")
            file_url = f'https://api.github.com/repos/{github_username}/{repository_name}/contents/{file_path}'
            file_params = {
                'message': commit_message,
                'content': file_content,
                'branch': head_branch
            }
            file_response = requests.put(file_url, json=file_params, headers=headers)


            if file_response.status_code == 201:
                print('File content uploaded successfully.')
            elif file_response.status_code == 422:
                print('File already exists')
            else:
                print('Failed to upload file content:', file_response.json()['message'])


            # Create a pull request
            pull_request_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/pulls'
            pull_request_params = {
                'title': f'Pull request by {github_username}', #You can change the pull request and 
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

            if((pr_response.status_code==201 or pr_response.status_code==422) and file_response.status_code==201):
                return "Pull request to add file has been created"
            else:
                return "Error occured"
            
        except Exception as err:
            return f"Error: {err}"