import openai
from openai import APIError, InvalidRequestError
from openai.error import RateLimitError, AuthenticationError, Timeout, TryAgain
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm

MAX_RETRY_ATTEMPTS = 5
MIN_WAIT = 30  # Seconds
MAX_WAIT = 300  # Seconds

MINIMAX_API_BASE = "https://api.minimax.io/v1"


def custom_retry_error_callback(retry_state):
    logger.info("MiniMax Exception:", retry_state.outcome.exception())
    return {"error": "ERROR_MINIMAX", "message": "MiniMax exception: " + str(retry_state.outcome.exception())}


class MiniMax(BaseLlm):
    def __init__(self, api_key, model="MiniMax-M3", temperature=0.6, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"),
                 top_p=1, frequency_penalty=0, presence_penalty=0, number_of_results=1):
        """
        Args:
            api_key (str): The MiniMax API key.
            model (str): The model name (e.g. MiniMax-M3, MiniMax-M2.7, MiniMax-M2.7-highspeed).
            temperature (float): The temperature. Must be in (0.0, 1.0].
            max_tokens (int): The maximum number of tokens.
            top_p (float): The top p.
            frequency_penalty (float): The frequency penalty.
            presence_penalty (float): The presence penalty.
            number_of_results (int): The number of results.
        """
        self.model = model
        # MiniMax rejects temperature=0; clamp to a small positive value
        self.temperature = max(temperature, 0.01) if temperature <= 0 else temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.number_of_results = number_of_results
        self.api_key = api_key

    def get_source(self):
        return "minimax"

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
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_random_exponential(min=MIN_WAIT, max=MAX_WAIT),
        before_sleep=lambda retry_state: logger.info(
            f"{retry_state.outcome.exception()} (attempt {retry_state.attempt_number})"),
        retry_error_callback=custom_retry_error_callback
    )
    def chat_completion(self, messages, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT")):
        """
        Call the MiniMax chat completion API (OpenAI-compatible).

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        try:
            # Point to MiniMax's OpenAI-compatible endpoint
            openai.api_key = self.api_key
            openai.api_base = MINIMAX_API_BASE

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
            logger.info("MiniMax RateLimitError:", api_error)
            raise RateLimitError(str(api_error))
        except Timeout as timeout_error:
            logger.info("MiniMax Timeout:", timeout_error)
            raise Timeout(str(timeout_error))
        except TryAgain as try_again_error:
            logger.info("MiniMax TryAgain:", try_again_error)
            raise TryAgain(str(try_again_error))
        except AuthenticationError as auth_error:
            logger.info("MiniMax AuthenticationError:", auth_error)
            return {"error": "ERROR_AUTHENTICATION",
                    "message": "Authentication error please check the api keys: " + str(auth_error)}
        except InvalidRequestError as invalid_request_error:
            logger.info("MiniMax InvalidRequestError:", invalid_request_error)
            return {"error": "ERROR_INVALID_REQUEST",
                    "message": "MiniMax invalid request error: " + str(invalid_request_error)}
        except Exception as exception:
            logger.info("MiniMax Exception:", exception)
            return {"error": "ERROR_MINIMAX", "message": "MiniMax exception: " + str(exception)}

    def verify_access_key(self):
        """
        Verify the access key is valid by making a lightweight chat request.

        Returns:
            bool: True if the access key is valid, False otherwise.
        """
        try:
            openai.api_key = self.api_key
            openai.api_base = MINIMAX_API_BASE
            openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            return True
        except AuthenticationError:
            return False
        except Exception as exception:
            logger.info("MiniMax Exception:", exception)
            return False

    def get_models(self):
        """
        Get the available MiniMax models.

        Returns:
            list: The models.
        """
        try:
            return ['MiniMax-M3', 'MiniMax-M2.7', 'MiniMax-M2.7-highspeed']
        except Exception as exception:
            logger.info("MiniMax Exception:", exception)
            return []
