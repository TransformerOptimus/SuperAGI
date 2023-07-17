import base64
import re

import requests
from superagi.lib.logger import logger


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
        # Strip any trailing slashes from the folder path
        folder_path = folder_path.rstrip('/')
        # Construct the file path
        file_path = f'{folder_path}/{file_name}'
        return file_path

    # Rest of the methods remain the same...
