import os
import requests
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm


class Replicate(BaseLlm):
    def __init__(self, api_key, model: str = None, version: str = None, max_length=1000, temperature=0.7,
                 candidate_count=1, top_k=40, top_p=0.95):
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
        self.version = version
        self.temperature = temperature
        self.candidate_count = candidate_count
        self.top_k = top_k
        self.top_p = top_p
        self.api_key = api_key
        self.max_length = max_length

    def get_source(self):
        return "replicate"

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

    def chat_completion(self, messages, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT") or 800):
        """
        Call the Replicate model API.

        Args:
            context (str): The context.
            messages (list): The messages.

        Returns:
            dict: The response.
        """
        prompt = "\n".join([message["role"] + ": " + message["content"] + "" for message in messages])

        if len(messages) == 1:
            prompt = "System:" + messages[0]['content'] + "\nResponse:"
        else:
            prompt = prompt + "\nResponse:"
        try:
            os.environ["REPLICATE_API_TOKEN"] = self.api_key
            import replicate
            output_generator = replicate.run(
                self.model + ":" + self.version,
                input={"prompt": prompt, "max_length": 40000, "temperature": self.temperature,
                       "top_p": self.top_p}
            )

            final_output = ""
            temp_output = []
            for item in output_generator:
                final_output += item
                temp_output.append(item)

            if not final_output:
                logger.error("Replicate model didn't return any output.")
                return {"error": "Replicate model didn't return any output."}
            print(final_output)
            print(temp_output)
            logger.info("Replicate response:", final_output)

            return {"response": temp_output, "content": final_output}
        except Exception as exception:
            logger.error('Replicate model ' + self.model + ' Exception:', exception)
            return {"error": exception}

    def verify_access_key(self):
        """
        Verify the access key is valid.

        Returns:
            bool: True if the access key is valid, False otherwise.
        """
        headers = {"Authorization": "Token " + self.api_key}
        response = requests.get("https://api.replicate.com/v1/collections", headers=headers)

        # If the request is successful, status code will be 200
        if response.status_code == 200:
            return True
        else:
            return False

