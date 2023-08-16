import base64
import re

import requests
from superagi.lib.logger import logger
from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.types.storage_types import StorageType
from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper


class GithubHelper:
    def __init__(self, github_access_token, github_username):
        """
        Initializes the GithubHelper with the provided access token and username.

        Args:
            github_access_token (str): Personal GitHub access token.
            github_username (str): GitHub username.
        """
        self.github_access_token = github_access_token
        self.github_username = github_username

    def get_file_path(self, file_name, folder_path):
        """
        Returns the path of the given file with respect to the specified folder.

        Args:
            file_name (str): Name of the file.
            folder_path (str): Path to the folder.

        Returns:
            str: Combined file path.
        """
        file_path = f'{folder_path}'
        if folder_path:
            file_path += '/'
        file_path += file_name
        return file_path

    def check_repository_visibility(self, repository_owner, repository_name):
        """
        Checks the visibility (public/private) of a given repository.


        Args:
            repository_owner (str): Owner of the repository.
            repository_name (str): Name of the repository.

        Returns:
            bool: True if the repository is private, False if it's public.
        """
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
            logger.info(f"Failed to fetch repository information: {response.status_code} - {response.text}")
            return None

    def search_repo(self, repository_owner, repository_name, file_name, folder_path=None):
        """
        Searches for a file in the given repository and returns the file's metadata.

        Args:
            repository_owner (str): Owner of the repository.
            repository_name (str): Name of the repository.
            file_name (str): Name of the file to search for.
            folder_path (str, optional): Path to the folder containing the file. Defaults to None.

        Returns:
            dict: File metadata.
        """
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
        """
        Syncs the head branch with the base branch.

        Args:
            repository_owner (str): Owner of the repository.
            repository_name (str): Name of the repository.
            base_branch (str): Base branch to sync with.
            head_branch (str): Head branch to sync.
            headers (dict): Request headers.

        Returns:
            None
        """
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
            logger.info(
                f'Successfully synced {self.github_username}:{head_branch} branch with {repository_owner}:{base_branch}')
        else:
            logger.info('Failed to sync the branch. Check your inputs and permissions.')

    def make_fork(self, repository_owner, repository_name, base_branch, headers):
        """
        Creates a fork of the given repository.

        Args:
            repository_owner (str): Owner of the repository.
            repository_name (str): Name of the repository.
            base_branch (str): Base branch to sync with.
            headers (dict): Request headers.

        Returns:
            int: Status code of the fork request.
        """
        fork_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/forks'
        fork_response = requests.post(fork_url, headers=headers)
        if fork_response.status_code == 202:
            logger.info('Fork created successfully.')
            self.sync_branch(repository_owner, repository_name, base_branch, base_branch, headers)
        else:
            logger.info('Failed to create the fork:', fork_response.json()['message'])

        return fork_response.status_code

    def create_branch(self, repository_name, base_branch, head_branch, headers):
        """
        Creates a new branch in the given repository.

        Args:
            repository_name (str): Name of the repository.
            base_branch (str): Base branch to sync with.
            head_branch (str): Head branch to sync.
            headers (dict): Request headers.

        Returns:
            int: Status code of the branch creation request.
        """
        branch_url = f'https://api.github.com/repos/{self.github_username}/{repository_name}/git/refs'
        branch_params = {
            'ref': f'refs/heads/{head_branch}',
            'sha': requests.get(
                f'https://api.github.com/repos/{self.github_username}/{repository_name}/git/refs/heads/{base_branch}',
                headers=headers).json()['object']['sha']
        }
        branch_response = requests.post(branch_url, json=branch_params, headers=headers)
        if branch_response.status_code == 201:
            logger.info('Branch created successfully.')
        elif branch_response.status_code == 422:
            logger.info('Branch new-file already exists, making commits to new-file branch')
        else:
            logger.info('Failed to create branch:', branch_response.json()['message'])

        return branch_response.status_code

    def delete_file(self, repository_name, file_name, folder_path, commit_message, head_branch, headers):
        """
        Deletes a file or folder from the given repository.

        Args:
            repository_name (str): Name of the repository.
            file_name (str): Name of the file to delete.
            folder_path (str): Path to the folder containing the file.
            commit_message (str): Commit message.
            head_branch (str): Head branch to sync.
            headers (dict): Request headers.

        Returns:
            int: Status code of the file deletion request.
        """
        file_path = self.get_file_path(file_name, folder_path)
        file_url = f'https://api.github.com/repos/{self.github_username}/{repository_name}/contents/{file_path}'
        file_params = {
            'message': commit_message,
            'sha': self.get_sha(self.github_username, repository_name, file_name, folder_path),
            'branch': head_branch
        }
        file_response = requests.delete(file_url, json=file_params, headers=headers)
        if file_response.status_code == 200:
            logger.info('File or folder delete successfully.')
        else:
            logger.info('Failed to Delete file or folder:', file_response.json())

        return file_response.status_code

    def add_file(self, repository_owner, repository_name, file_name, folder_path, head_branch, base_branch, headers, commit_message, agent_id, agent_execution_id, session):
        """
        Adds a file to the given repository.

        Args:
            repository_owner (str): Owner of the repository.
            repository_name (str): Name of the repository.
            file_name (str): Name of the file to add.
            folder_path (str): Path to the folder containing the file.
            head_branch (str): Head branch to sync.
            base_branch (str): Base branch to sync with.

        Returns:
            None
        """
        body = self._get_file_content(file_name, agent_id, agent_execution_id, session)
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
            logger.info('File content uploaded successfully.')
        elif file_response.status_code == 422:
            logger.info('File already exists')
        else:
            logger.info('Failed to upload file content:', file_response.json()['message'])
        return file_response.status_code

    def create_pull_request(self, repository_owner, repository_name, head_branch, base_branch, headers):
        """
        Creates a pull request in the given repository.

        Args:
            repository_owner (str): Owner of the repository.
            repository_name (str): Name of the repository.
            head_branch (str): Head branch to sync.
            base_branch (str): Base branch to sync with.
            headers (dict): Request headers.

        Returns:
            int: Status code of the pull request creation request.
        """
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
            logger.info('Pull request created successfully.')
        elif pr_response.status_code == 422:
            logger.info('Added changes to already existing pull request')
        else:
            logger.info('Failed to create pull request:', pr_response.json()['message'])

        return pr_response.status_code

    def get_sha(self, repository_owner, repository_name, file_name, folder_path=None):
        """
        Gets the sha of the file to be deleted.

        Args:
            repository_owner (str): Owner of the repository.
            repository_name (str): Name of the repository.
            file_name (str): Name of the file to delete.
            folder_path (str): Path to the folder containing the file.

        Returns:
            str: Sha of the file to be deleted.
        """
        data = self.search_repo(repository_owner, repository_name, file_name, folder_path)
        return data['sha']

    def get_content_in_file(self, repository_owner, repository_name, file_name, folder_path=None):
        """
        Gets the content of the file.

        Args:
            repository_owner (str): Owner of the repository.
            repository_name (str): Name of the repository.
            file_name (str): Name of the file to delete.
            folder_path (str): Path to the folder containing the file.

        Returns:
            str: Content of the file.
        """
        data = self.search_repo(repository_owner, repository_name, file_name, folder_path)
        file_content = data['content']
        file_content_encoding = data.get('encoding')
        if file_content_encoding == 'base64':
            file_content = base64.b64decode(file_content).decode()

        return file_content

    @classmethod
    def validate_github_link(cls, link: str) -> bool:
        """
        Validate a GitHub link.
        Returns True if the link is valid, False otherwise.
        """
        # Regular expression pattern to match a GitHub link
        pattern = r'^https?://(?:www\.)?github\.com/[\w\-]+/[\w\-]+$'

        # Check if the link matches the pattern
        if re.match(pattern, link):
            return True

        return False

    def _get_file_contents(self, file_name, agent_id, agent_execution_id, session):
        final_path = ResourceHelper().get_agent_read_resource_path(file_name,
                                                                    agent=Agent.get_agent_from_id(session, agent_id),
                                                                    agent_execution=AgentExecution.get_agent_execution_from_id(
                                                                  session, agent_execution_id))
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
                attachment_data = S3Helper().read_from_s3(final_path)
        else:
            with open(final_path, "r") as file:
                attachment_data = file.read().decode('utf-8')
        return attachment_data
