import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import json



from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm


class CustomLLM(BaseLlm):
    def __init__(self, api_key="null", model="gpt-4", temperature=0.6, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"), top_p=1,
                 frequency_penalty=0,
                 presence_penalty=0, number_of_results=1):
        """
        Args:
            api_key (str): The OpenAI API key.
            model (str): The model.
            temperature (float): The temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The top p.
            frequency_penalty (float): The frequency penalty.
            presence_penalty (float): The presence penalty.
            number_of_results (int): The number of results.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.number_of_results = number_of_results
        self.api_key = api_key

    def get_source(self):
        return "custom"

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

    def chat_completion(self, messages, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT")):


        """
        Call custom LLM node.


        Returns:
            dict: The response.
        """


        url = "http://gpt4free:5000"  # replace <DOCKER_SERVER_IP> with the IP address of your Docker server - todo, make that in config

        # Prepare the data payload for the POST request
        data = {"message": messages}

        # Make the POST request to the Docker server
        response = requests.post(url, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            content = response_data.get("response")#Currently just in response is content only
            return {"response": "", "content": json.dumps(content)}
        else:
        # Handle the error (you can customize this part according to your needs)
            return {"error": "Failed to get a response from the Docker server."}



    def verify_access_key(self):
        """
        todo - conectivity handling here
        """
        return True


    def get_models(self):
        """
        Get the models.

        Returns:
            list: The models.
        """
        try:
            models_supported = ['custom_todo-model_support']
            return models_supported
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)#todo - better error handling
            return []
