from typing import List

import tiktoken

from superagi.types.common import BaseMessage
from superagi.lib.logger import logger


class TokenCounter:
    @staticmethod
    def token_limit(model: str = "gpt-3.5-turbo-0301") -> int:
        """
        Function to return the token limit for a given model.

        Args:
            model (str): The model to return the token limit for.

        Raises:
            KeyError: If the model is not found.

        Returns:
            int: The token limit.
        """
        try:
            model_token_limit_dict = {"gpt-3.5-turbo-0301": 4032, "gpt-4-0314": 8092, "gpt-3.5-turbo": 4032,
                                      "gpt-4": 8092, "gpt-3.5-turbo-16k": 16184, "gpt-4-32k": 32768,
                                      "gpt-4-32k-0314": 32768, "models/chat-bison-001": 8092}
            return model_token_limit_dict[model]
        except KeyError:
            logger.warning("Warning: model not found. Using cl100k_base encoding.")
            return 8092

    @staticmethod
    def count_message_tokens(messages: List[BaseMessage], model: str = "gpt-3.5-turbo-0301") -> int:
        """
        Function to count the number of tokens in a list of messages.

        Args:
            messages (List[BaseMessage]): The list of messages to count the tokens for.
            model (str): The model to count the tokens for.

        Raises:
            KeyError: If the model is not found.

        Returns:
            int: The number of tokens in the messages.
        """
        try:
            default_tokens_per_message = 4
            model_token_per_message_dict = {"gpt-3.5-turbo-0301": 4, "gpt-4-0314": 3, "gpt-3.5-turbo": 4, "gpt-4": 3,
                                            "gpt-3.5-turbo-16k": 4, "gpt-4-32k": 3, "gpt-4-32k-0314": 3,
                                            "models/chat-bison-001": 4}
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        if model in model_token_per_message_dict.keys():
            tokens_per_message = model_token_per_message_dict[model]
        else:
            tokens_per_message = default_tokens_per_message

        if tokens_per_message is None:
            raise NotImplementedError(
                f"num_tokens_from_messages() is not implemented for model {model}.\n"
                " See https://github.com/openai/openai-python/blob/main/chatml.md for"
                " information on how messages are converted to tokens."
            )

        num_tokens = 0
        for message in messages:
            if isinstance(message, str):
                message = {'content': message}
            num_tokens += tokens_per_message
            num_tokens += len(encoding.encode(message['content']))

        num_tokens += 3
        return num_tokens

    @staticmethod
    def count_text_tokens(message: str) -> int:
        """
        Function to count the number of tokens in a text.

        Args:
            message (str): The text to count the tokens for.

        Returns:
            int: The number of tokens in the text.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(message)) + 4
        return num_tokens
