import openai
from openai import APIError, InvalidRequestError
from openai.error import RateLimitError, AuthenticationError
import litellm 
from litellm import completion 
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm


class Lite(BaseLlm):
    def __init__(self, api_key, model="gpt-4", temperature=0.6, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"), top_p=1,
                 frequency_penalty=0,
                 presence_penalty=0, number_of_results=1):
        """
        Args:
            api_key (str): The LLM API key for Anthropic/Cohere/Azure/Replicate.
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
        litellm.api_base = get_config("OPENAI_API_BASE", None)

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
        Call any LLM Provider (Anthropic/Cohere/Azure/Replicate) with the same params as the OpenAI API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        try:
            # openai.api_key = get_config("OPENAI_API_KEY")
            response = completion(
                n=self.number_of_results,
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )
            content = response["choices"][0]["message"]["content"]
            return {"response": response, "content": content}
        except AuthenticationError as auth_error:
            logger.info("LLM AuthenticationError:", auth_error)
            return {"error": "ERROR_AUTHENTICATION", "message": "Authentication error please check the api keys.."}
        except RateLimitError as api_error:
            logger.info("LLM RateLimitError:", api_error)
            return {"error": "ERROR_RATE_LIMIT", "message": "LLM rate limit exceeded.."}
        except InvalidRequestError as invalid_request_error:
            logger.info("LLM InvalidRequestError:", invalid_request_error)
            return {"error": "ERROR_INVALID_REQUEST", "message": "LLM invalid request error.."}
        except Exception as exception:
            logger.info("LLM Exception:", exception)
            return {"error": "ERROR_LLM", "message": "Open ai exception"}

    def verify_access_key(self):
        """
        Verify the access key is valid.

        Returns:
            bool: True if the access key is valid, False otherwise.
        """
        try:
            models = openai.Model.list()
            return True
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)
            return False

    def get_models(self):
        """
        Get the models.

        Returns:
            list: The models.
        """
        try:
            return litellm.model_list
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)
            return []
