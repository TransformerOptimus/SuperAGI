import openai

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm


class OpenAi(BaseLlm):
    def __init__(self, api_key, model="gpt-4", temperature=0.6, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"), top_p=1,
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
        openai.api_key = api_key
        openai.api_base = get_config("OPENAI_API_BASE", "https://api.openai.com/v1")

    def get_source(self):
        return "openai"

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
        Call the OpenAI chat completion API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        try:
            # openai.api_key = get_config("OPENAI_API_KEY")
            response = openai.ChatCompletion.create(
                n=self.number_of_results,
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )
            content = response.choices[0].message["content"]
            return {"response": response, "content": content}
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)
            return {"error": exception}
