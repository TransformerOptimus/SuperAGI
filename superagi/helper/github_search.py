import requests
import time

import base64
import json
import os

from pydantic import BaseModel
from github import Github

from superagi.helper.webpage_extractor import WebpageExtractor


class GithubHelper:

    def __init__(self,github_access_token,github_username):
        self.github_access_token=github_access_token
        self.github_username=github_username

    def get_repository_collaborators(self,repository_owner,repository_name,user_to_check):
        url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/collaborators'
        # Send the GET request to retrieve the collaborators list
        response = requests.get(url, headers={'Authorization': f'token {self.github_access_token}'})
        
        try:
            if response.status_code == 200:
                collaborators = response.json()
                collaborator_logins = [collaborator['login'] for collaborator in collaborators]
                if user_to_check in collaborator_logins:
                    print(f'{user_to_check} is a collaborator of the repository.')
                    return True
                else:
                    print(f'{user_to_check} is not a collaborator of the repository.')
            else:
                # print(response.status_code)
                print('Failed to retrieve the collaborators list:', response.json()['message'])
        except Exception as err:
            print(f"Error: {err}")
            
        return False

    def search_repo(self,repository_owner,repository_name,file_name,folder_path):
        headers={
            "Authorization": f"token {self.github_access_token}" if self.github_access_token else None,
            "Content-Type": "application/vnd.github+json"
        }  
        if folder_path:
                folder_path+='/'
        file_path=f'{folder_path}{file_name}'
        url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/contents/{file_path}'
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()

        return data
        
    def get_sha(self,repository_owner,repository_name,file_name,folder_path):
        data=self.search_repo(repository_owner,repository_name,file_name,folder_path)
        return data['sha']
        
    def get_content_in_file(self,repository_owner,repository_name,file_name,folder_path):
        data=self.search_repo(repository_owner,repository_name,file_name,folder_path)
        file_content = data['content']
        file_content_encoding = data.get('encoding')
        if file_content_encoding == 'base64':
            file_content = base64.b64decode(file_content).decode()

        return file_content