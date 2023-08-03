import os
import requests
import json
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm

class HuggingFace(BaseLlm):
    def __init__(
            self,
            api_key,
            end_point: '',
#             model: HuggingFaceEndpoints = HuggingFaceEndpoints.FALCON_7B,
#             task: Task = Task.TEXT_GENERATION,
#             **kwargs
        ):
            """
            Args:
                api_key (str): The HuggingFace Bearer token.
                model (str): The model id.
                task (Task): The task to perform.
                **kwargs: The task parameters. If not provided, the default parameters will be used.
            """
#             self.model = model
            self.api_key = api_key
            self.end_point = end_point
#             self.task = task
#             self.task_params = TaskParamters().get_params(self.task, **kwargs)
#             self.API_URL = model.value
#             self.VALIDATION_URL = "https://huggingface.co/api/models"
#             self.headers = {
#                 "Authorization": f"Bearer {self.api_key}",
#                 "Content-Type": "application/json",
#             }

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
        The API needs a POST request with the parameter "inputs".

        Args:
            inputs (dict): The inputs to send over POST.

        Returns:
            dict: The model.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = json.dumps({"inputs": "validating end_point"})
        response = requests.post(self.end_point, headers=headers, data=data)
        model = response.json()

        return model

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

    def chat_completion(self, messages, max_tokens=100):
        """
        Call the HuggingFace inference API.
        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.
        Returns:
            dict: The response.
        """
#         try:
#             params = self.task_params
#             if self.task == Task.TEXT_GENERATION:
#                 params["max_new_tokens"] = max_tokens
#             elif self.task == Task.SUMMARIZATION:
#                 params["max_length"] = max_tokens
#             payload = {
#                 "inputs": messages,
#                 "parameters": self.task_params,
#                 "options": {
#                     "use_cache": False,
#                     "wait_for_model": True,
#                 }
#             }
#             response = requests.post(self.API_URL, headers=self.headers, data=json.dumps(payload))
#             completion = json.loads(response.content.decode("utf-8"))
#             if self.task == Task.TEXT_GENERATION:
#                 content = completion[0]["generated_text"]
#             elif self.task == Task.SUMMARIZATION:
#                 content = completion[0]["summary_text"]
#             else:
#                 content = completion[0]["answer"]
#
#             return {"response": completion, "content": content}
#         except Exception as exception:
#             print(exception)
#             # logger.info("HF Exception:", exception)
#             return {"error": "ERROR_HUGGINGFACE", "message": "HuggingFace Inference exception"}
        pass