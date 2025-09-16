try:
    import anthropic
    from anthropic import APIError, AuthenticationError, RateLimitError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    # Create mock classes for when anthropic is not installed
    class APIError(Exception):
        pass
    class AuthenticationError(Exception):
        pass
    class RateLimitError(Exception):
        pass

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm


class Anthropic(BaseLlm):
    def __init__(self, api_key, model="claude-3-5-sonnet-20241022", temperature=0.6, max_tokens=8192):
        """
        Args:
            api_key (str): The Anthropic API key.
            model (str): The model.
            temperature (float): The temperature.
            max_tokens (int): The maximum number of tokens.
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package is required for Anthropic LLM support. Install it with: pip install anthropic")
            
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)

    def get_source(self):
        return "anthropic"

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

    def chat_completion(self, messages, max_tokens=None):
        """
        Call the Anthropic Claude chat completion API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """
        try:
            # Convert OpenAI format messages to Anthropic format
            anthropic_messages = []
            system_message = ""
            
            for message in messages:
                if message["role"] == "system":
                    system_message = message["content"]
                else:
                    anthropic_messages.append({
                        "role": message["role"],
                        "content": message["content"]
                    })

            # Use provided max_tokens or instance default
            token_limit = max_tokens or self.max_tokens

            # Create completion
            if system_message:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=token_limit,
                    temperature=self.temperature,
                    system=system_message,
                    messages=anthropic_messages
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=token_limit,
                    temperature=self.temperature,
                    messages=anthropic_messages
                )

            content = response.content[0].text
            return {"response": response, "content": content}
            
        except RateLimitError as rate_error:
            logger.info("Anthropic RateLimitError:", rate_error)
            return {"error": "ERROR_RATE_LIMIT", "message": "Rate limit exceeded: " + str(rate_error)}
        except AuthenticationError as auth_error:
            logger.info("Anthropic AuthenticationError:", auth_error)
            return {"error": "ERROR_AUTHENTICATION", "message": "Authentication error: " + str(auth_error)}
        except APIError as api_error:
            logger.info("Anthropic APIError:", api_error)
            return {"error": "ERROR_API", "message": "API error: " + str(api_error)}
        except Exception as exception:
            logger.info("Anthropic Exception:", exception)
            return {"error": "ERROR_ANTHROPIC", "message": "Anthropic exception: " + str(exception)}

    def verify_access_key(self):
        """
        Verify the access key is valid.

        Returns:
            bool: True if the access key is valid, False otherwise.
        """
        try:
            # Test with a minimal message
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as exception:
            logger.info("Anthropic access key verification failed:", exception)
            return False

    def get_models(self):
        """
        Get the supported models.

        Returns:
            list: The models.
        """
        try:
            # Return list of supported Claude models
            models_supported = [
                # Claude 3.5 series (latest and recommended)
                'claude-3-5-sonnet-20241022', 'claude-3-5-sonnet-20240620', 'claude-3-5-haiku-20241022',
                # Claude 3 series
                'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307',
                # Claude 2 series (legacy but still supported)
                'claude-2.1', 'claude-2.0', 'claude-instant-1.2'
            ]
            return models_supported
        except Exception as exception:
            logger.info("Anthropic Exception:", exception)
            return []