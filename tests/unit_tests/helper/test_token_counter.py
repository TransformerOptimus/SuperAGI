import pytest

from typing import List
from superagi.helper.token_counter import TokenCounter
from superagi.types.common import BaseMessage
from unittest.mock import MagicMock


def test_token_limit():
    assert TokenCounter.token_limit("gpt-3.5-turbo-0301") == 4032
    assert TokenCounter.token_limit("gpt-4-0314") == 8092
    assert TokenCounter.token_limit("gpt-3.5-turbo") == 4032
    assert TokenCounter.token_limit("gpt-4") == 8092
    assert TokenCounter.token_limit("gpt-3.5-turbo-16k") == 16184
    assert TokenCounter.token_limit("gpt-4-32k") == 32768
    assert TokenCounter.token_limit("gpt-4-32k-0314") == 32768
    assert TokenCounter.token_limit("non_existing_model") == 8092




def test_count_message_tokens():
    # Using MagicMock to create mock objects mimicking BaseMessage behavior
    message1 = MagicMock(role="system", content="You are a helpful assistant.")
    message2 = MagicMock(role="user", content="What is your name?")
    messages = [message1]
    
    # Run the test with only one message
    assert TokenCounter.count_message_tokens(messages, "gpt-3.5-turbo-0301") == 11
    assert TokenCounter.count_message_tokens(messages, "gpt-4-0314") == 10
    assert TokenCounter.count_message_tokens(messages, "gpt-3.5-turbo") == 11
    assert TokenCounter.count_message_tokens(messages, "gpt-4") == 10
    assert TokenCounter.count_message_tokens(messages, "gpt-3.5-turbo-16k") == 11
    assert TokenCounter.count_message_tokens(messages, "gpt-4-32k") == 10
    assert TokenCounter.count_message_tokens(messages, "gpt-4-32k-0314") == 10
    assert TokenCounter.count_message_tokens(messages, "non_existing_model") == 10
    
    messages = [message1, message2]
    
    # Run the test with two messages
    assert TokenCounter.count_message_tokens(messages, "gpt-3.5-turbo-0301") == 20
    assert TokenCounter.count_message_tokens(messages, "gpt-4-0314") == 17
    assert TokenCounter.count_message_tokens(messages, "non_existing_model") == 17


def test_count_text_tokens():
    # You might need to adjust the hardcoded values in the TokenCounter.count_text_tokens function
    # and update the expected tokens accordingly if the function logic is changed.

    text = "You are a helpful assistant."
    assert TokenCounter.count_text_tokens(text) == 10

    text = "What is your name?"
    assert TokenCounter.count_text_tokens(text) == 8