import requests
import time

import base64
import json
import os

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

    def check_repository_visibility(self, repository_owner, repository_name):
        url = f"https://api.github.com/repos/{repository_owner}/{repository_name}"
        headers = {
            "Authorization": f"Token {self.github_access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            repository_data = response.json()
            return repository_data['private']
        else:
            print(f"Failed to fetch repository information: {response.status_code} - {response.text}")
            return None

    def search_repo(self,repository_owner,repository_name,file_name,folder_path=None):
        headers={
            "Authorization": f"token {self.github_access_token}" if self.github_access_token else None,
            "Content-Type": "application/vnd.github+json"
        }  
        file_path=f'{folder_path}'
        if folder_path:
            file_path+='/'
        file_path+=file_name
        url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/contents/{file_path}'
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()

        return data
    
    def sync_branch(self,repository_owner,repository_name,base_branch,head_branch):
        # Get the base branch commit SHA
        headers={
            "Authorization": f"token {self.github_access_token}" if self.github_access_token else None,
            "Content-Type": "application/vnd.github+json"
        }  
        base_branch_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/branches/{base_branch}'
        response = requests.get(base_branch_url, headers=headers)
        response_json = response.json()
        base_commit_sha = response_json['commit']['sha']
        # Update the head branch with the base branch commit SHA
        head_branch_url = f'https://api.github.com/repos/{self.github_username}/{repository_name}/git/refs/heads/{head_branch}'
        data = {
            'sha': base_commit_sha,
            'force': True
        }
        response = requests.patch(head_branch_url, json=data, headers=headers)
        if response.status_code == 200:
            print(f'Successfully synced {self.github_username}:{head_branch} branch with {repository_owner}:{base_branch}')
        else:
            print('Failed to sync the branch. Check your inputs and permissions.')

        # syncing base_branch in forked repository
        # head_branch_url = f'https://api.github.com/repos/{self.github_username}/{repository_name}/git/refs/heads/{base_branch}'
        # data = {
        #     'sha': base_commit_sha,
        #     'force': True
        # }
        # response = requests.patch(head_branch_url, json=data, headers=headers)
        # if response.status_code == 200:
        #     print(f'Successfully synced {self.github_username}:{base_branch} branch with {repository_owner}:{base_branch}')
        # else:
        #     print('Failed to sync the branch. Check your inputs and permissions.')


    def get_sha(self,repository_owner,repository_name,file_name,folder_path=None):
        data=self.search_repo(repository_owner,repository_name,file_name,folder_path)
        return data['sha']
    
    # def get_default_branch(self,repository_owner,repository_name)->str:
    #     headers={
    #         "Authorization": f"token {self.github_access_token}" if self.github_access_token else None,
    #         "Content-Type": "application/vnd.github+json"
    #     }
    #     url = f"https://api.github.com/repos/{repository_owner}/{repository_name}"
    #     response = requests.get(url, headers=headers)
    #     if response.status_code == 200:
    #         repo_details = response.json()
    #         base_branch = repo_details["default_branch"]
    #         print(f"The base branch of {repository_owner}/{repository_name} is: {base_branch}")
    #         return base_branch
    #     else:
    #         print(f"Error fetching repository details: {response.status_code} - {response.text}")
        
    #     return None

    def get_content_in_file(self,repository_owner,repository_name,file_name,folder_path=None):
        data=self.search_repo(repository_owner,repository_name,file_name,folder_path)
        file_content = data['content']
        file_content_encoding = data.get('encoding')
        if file_content_encoding == 'base64':
            file_content = base64.b64decode(file_content).decode()

        return file_content