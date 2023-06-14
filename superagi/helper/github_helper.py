import base64
import requests


class GithubHelper:
    def __init__(self, github_access_token, github_username):
        self.github_access_token = github_access_token
        self.github_username = github_username

    def get_file_path(self, file_name, folder_path):
        file_path = f'{folder_path}'
        if folder_path:
            file_path += '/'
        file_path += file_name
        return file_path

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

    def search_repo(self, repository_owner, repository_name, file_name, folder_path=None):
        headers = {
            "Authorization": f"token {self.github_access_token}" if self.github_access_token else None,
            "Content-Type": "application/vnd.github+json"
        }
        file_path = self.get_file_path(file_name, folder_path)
        url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/contents/{file_path}'
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()

        return data

    def sync_branch(self, repository_owner, repository_name, base_branch, head_branch, headers):
        base_branch_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/branches/{base_branch}'
        response = requests.get(base_branch_url, headers=headers)
        response_json = response.json()
        base_commit_sha = response_json['commit']['sha']
        head_branch_url = f'https://api.github.com/repos/{self.github_username}/{repository_name}/git/refs/heads/{head_branch}'
        data = {
            'sha': base_commit_sha,
            'force': True
        }
        response = requests.patch(head_branch_url, json=data, headers=headers)
        if response.status_code == 200:
            print(
                f'Successfully synced {self.github_username}:{head_branch} branch with {repository_owner}:{base_branch}')
        else:
            print('Failed to sync the branch. Check your inputs and permissions.')

    def make_fork(self, repository_owner, repository_name, base_branch, headers):
        fork_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/forks'
        fork_response = requests.post(fork_url, headers=headers)
        if fork_response.status_code == 202:
            print('Fork created successfully.')
            self.sync_branch(repository_owner, repository_name, base_branch, base_branch, headers)
        else:
            print('Failed to create the fork:', fork_response.json()['message'])

        return fork_response.status_code

    def create_branch(self, repository_name, base_branch, head_branch, headers):
        branch_url = f'https://api.github.com/repos/{self.github_username}/{repository_name}/git/refs'
        branch_params = {
            'ref': f'refs/heads/{head_branch}',
            'sha': requests.get(
                f'https://api.github.com/repos/{self.github_username}/{repository_name}/git/refs/heads/{base_branch}',
                headers=headers).json()['object']['sha']
        }
        branch_response = requests.post(branch_url, json=branch_params, headers=headers)
        if branch_response.status_code == 201:
            print('Branch created successfully.')
        elif branch_response.status_code == 422:
            print('Branch new-file already exists, making commits to new-file branch')
        else:
            print('Failed to create branch:', branch_response.json()['message'])

        return branch_response.status_code

    def delete_file(self, repository_name, file_name, folder_path, commit_message, head_branch, headers):
        file_path = self.get_file_path(file_name, folder_path)
        file_url = f'https://api.github.com/repos/{self.github_username}/{repository_name}/contents/{file_path}'
        file_params = {
            'message': commit_message,
            'sha': self.get_sha(self.github_username, repository_name, file_name, folder_path),
            'branch': head_branch
        }
        file_response = requests.delete(file_url, json=file_params, headers=headers)
        if file_response.status_code == 200:
            print('File or folder delete successfully.')
        else:
            print('Failed to Delete file or folder:', file_response.json())

        return file_response.status_code

    def add_file(self, repository_owner, repository_name, file_name, folder_path, head_branch, base_branch, headers,
                 body, commit_message):
        body_bytes = body.encode("ascii")
        base64_bytes = base64.b64encode(body_bytes)
        file_content = base64_bytes.decode("ascii")
        file_path = self.get_file_path(file_name, folder_path)
        file_url = f'https://api.github.com/repos/{self.github_username}/{repository_name}/contents/{file_path}'
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
        return file_response.status_code

    def create_pull_request(self, repository_owner, repository_name, head_branch, base_branch, headers):
        pull_request_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/pulls'
        pull_request_params = {
            'title': f'Pull request by {self.github_username}',
            'body': 'Please review and merge this change.',
            'head': f'{self.github_username}:{head_branch}',  # required for cross repository only
            'head_repo': repository_name,  # required for cross repository only
            'base': base_branch
        }
        pr_response = requests.post(pull_request_url, json=pull_request_params, headers=headers)

        if pr_response.status_code == 201:
            print('Pull request created successfully.')
        elif pr_response.status_code == 422:
            print('Added changes to already existing pull request')
        else:
            print('Failed to create pull request:', pr_response.json()['message'])

        return pr_response.status_code

    def get_sha(self, repository_owner, repository_name, file_name, folder_path=None):
        data = self.search_repo(repository_owner, repository_name, file_name, folder_path)
        return data['sha']

    def get_content_in_file(self, repository_owner, repository_name, file_name, folder_path=None):
        data = self.search_repo(repository_owner, repository_name, file_name, folder_path)
        file_content = data['content']
        file_content_encoding = data.get('encoding')
        if file_content_encoding == 'base64':
            file_content = base64.b64decode(file_content).decode()

        return file_content
