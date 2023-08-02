import os
import requests
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm

class HuggingFace(BaseLlm):
    def __init__(self, api_key, model: str = None):
            """
            Args:
                api_key (str): The Replicate API key.
                model (str): The model.
                version (str): The version.
                temperature (float): The temperature.
                candidate_count (int): The number of candidates.
                top_k (int): The top k.
                top_p (float): The top p.
            """
            self.model = model
            self.api_key = api_key

    def get_source(self):
            return "hugging face"

    def get_api_key(self):
        """
        Returns:
            str: The API key.
        """
        return self.api_key

    def get_model(self):
            """
            Returns:
                str: The model.
            """
            return self.model

    def get_models(self):
        """
        Returns:
            str: The model.
        """
        return self.model

    def verify_access_key(self):
            """
            Verify the access key is valid.

            Returns:
                bool: True if the access key is valid, False otherwise.
            """
            headers = {"Authorization": "Bearer " + self.api_key}
            response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)

            # If the request is successful, status code will be 200
            if response.status_code == 200:
                return True
            else:
                return False

    def chat_completion():
        pass