import json
import requests

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm
from superagi.llms.utils.huggingface_tasks import Task, TaskParamters
from superagi.llms.utils.huggingface_endpoints import HuggingFaceEndpoints


class HuggingFace(BaseLlm):
    def __init__(
        self,
        api_key,
        model: HuggingFaceEndpoints = HuggingFaceEndpoints.FALCON_7B,
        task: Task = Task.TEXT_GENERATION,
        **kwargs
    ):
        """
        Args:
            api_key (str): The HuggingFace Bearer token.
            model (str): The model id.
            task (Task): The task to perform.
            **kwargs: The task parameters. If not provided, the default parameters will be used.
        """
        self.model = model
        self.api_key = api_key
        self.task = task
        self.task_params = TaskParamters().get_params(self.task, **kwargs)
        self.API_URL = model.value
        self.VALIDATION_URL = "https://huggingface.co/api/models"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_source(self):
        return "huggingface"

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

    def chat_completion(self, messages, max_tokens=100):
        """
        Call the HuggigFace inference API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        try:
            params = self.task_params
            if self.task == Task.TEXT_GENERATION:
                params["max_new_tokens"] = max_tokens
            elif self.task == Task.SUMMARIZATION:
                params["max_length"] = max_tokens
            payload = {
                "inputs": messages,
                "parameters": self.task_params,
                "options": {
                    "use_cache": False,
                    "wait_for_model": True,
                }
            }
            response = requests.post(self.API_URL, headers=self.headers, data=json.dumps(payload))
            completion = json.loads(response.content.decode("utf-8"))
            if self.task == Task.TEXT_GENERATION:
                content = completion[0]["generated_text"]
            elif self.task == Task.SUMMARIZATION:
                content = completion[0]["summary_text"]
            else:
                content = completion[0]["answer"]

            return {"response": completion, "content": content}
        except Exception as exception:
            print(exception)
            # logger.info("HF Exception:", exception)
            return {"error": "ERROR_HUGGINGFACE", "message": "HuggingFace Inference exception"}

    def verify_access_key(self):
        """
        Verify the access key is valid.

        Returns:
            bool: True if the access key is valid, False otherwise.
        """
        try:
            # Just send a dummy request to the API.
            # !IMPORTANT !IMPORTANT !IMPORTANT
            # This is a dummy check and it needs to be refactored to include tests for models not supporting **TEXT_GENERATION**.
            payload = {
                "inputs": ["Is this working?"],
            }
            response = requests.post(self.API_URL, headers=self.headers, data=json.dumps(payload))
            completion = json.loads(response.content.decode("utf-8"))
            # _ = completion[0]["generated_text"]
            return True
        except Exception as exception:
            print(exception)
            # logger.info("HuggingFace Exception:", exception)
            return False

    def get_models(self):
        # return a list of models from the Enum HuggingFaceModels
        return [model.name for model in HuggingFaceEndpoints]


if __name__ == "__main__":
    falcon_7b = HuggingFace(api_key="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")
    query = "How to make a cake?"
    print(f"Query: {query}")
    answer = falcon_7b.chat_completion(query)["content"]
    print(f"Response: {answer}")
