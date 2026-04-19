import openai
from openai import APIError, InvalidRequestError
from openai.error import RateLimitError, AuthenticationError, Timeout, TryAgain
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm

# Retry configuration for API calls
MAX_RETRY_ATTEMPTS = 5  # Maximum number of retry attempts for rate-limited or timeout errors
MIN_WAIT = 30  # Minimum wait time between retries in seconds
MAX_WAIT = 300  # Maximum wait time between retries in seconds

# Supported OpenAI models
SUPPORTED_MODELS = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo-preview"]

def custom_retry_error_callback(retry_state):
    """Callback function when retry limit is exceeded"""
    logger.error(f"OpenAI API Exception (max retries exceeded): {retry_state.outcome.exception()}")
    return {"error": "ERROR_OPENAI", "message": f"OpenAI exception: {str(retry_state.outcome.exception())}"}


class OpenAi(BaseLlm):
    def __init__(self, api_key, model="gpt-4", temperature=0.6, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"), top_p=1,
                 frequency_penalty=0,
                 presence_penalty=0, number_of_results=1):
        """
        Initialize OpenAI LLM client.
        
        Args:
            api_key (str): The OpenAI API key.
            model (str): The model name (e.g., 'gpt-4', 'gpt-3.5-turbo').
            temperature (float): Sampling temperature (0-2). Higher = more random.
            max_tokens (int): The maximum number of tokens in response.
            top_p (float): Nucleus sampling parameter (0-1).
            frequency_penalty (float): Penalty for token frequency (-2 to 2).
            presence_penalty (float): Penalty for token presence (-2 to 2).
            number_of_results (int): Number of completion choices to generate.
            
        Raises:
            ValueError: If model is not supported.
        """
        if model not in SUPPORTED_MODELS:
            logger.warning(f"Model '{model}' not in official supported list: {SUPPORTED_MODELS}. Proceeding anyway.")
        
        self.model = model
        self.temperature = max(0, min(2, temperature))  # Clamp temperature to valid range
        self.max_tokens = max_tokens
        self.top_p = max(0, min(1, top_p))  # Clamp top_p to valid range
        self.frequency_penalty = max(-2, min(2, frequency_penalty))  # Clamp penalty
        self.presence_penalty = max(-2, min(2, presence_penalty))  # Clamp penalty
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

    @retry(
        retry=(
            retry_if_exception_type(RateLimitError) |
            retry_if_exception_type(Timeout) |
            retry_if_exception_type(TryAgain)
        ),
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS), # Maximum number of retry attempts
        wait=wait_random_exponential(min=MIN_WAIT, max=MAX_WAIT),
        before_sleep=lambda retry_state: logger.info(f"{retry_state.outcome.exception()} (attempt {retry_state.attempt_number})"),
        retry_error_callback=custom_retry_error_callback
    )
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
        except RateLimitError as api_error:
            logger.info("OpenAi RateLimitError:", api_error)
            raise RateLimitError(str(api_error))
        except Timeout as timeout_error:
            logger.info("OpenAi Timeout:", timeout_error)
            raise Timeout(str(timeout_error))
        except TryAgain as try_again_error:
            logger.info("OpenAi TryAgain:", try_again_error)
            raise TryAgain(str(try_again_error))
        except AuthenticationError as auth_error:
            logger.info("OpenAi AuthenticationError:", auth_error)
            return {"error": "ERROR_AUTHENTICATION", "message": "Authentication error please check the api keys: "+str(auth_error)}
        except InvalidRequestError as invalid_request_error:
            logger.info("OpenAi InvalidRequestError:", invalid_request_error)
            return {"error": "ERROR_INVALID_REQUEST", "message": "Openai invalid request error: "+str(invalid_request_error)}
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)
            return {"error": "ERROR_OPENAI", "message": "Open ai exception: "+str(exception)}

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
            models = openai.Model.list()
            models = [model["id"] for model in models["data"]]
            models_supported = ['gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4-32k']
            models = [model for model in models if model in models_supported]
            return models
        except Exception as exception:
            logger.info("OpenAi Exception:", exception)
            return []
