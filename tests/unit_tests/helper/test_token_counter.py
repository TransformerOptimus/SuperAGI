import pytest

from typing import List
from unittest.mock import MagicMock, patch
from superagi.types.common import BaseMessage
from superagi.helper.token_counter import TokenCounter
from superagi.models.models import Models


@pytest.fixture()
def setup_model_token_limit():
    model_token_limit_dict = {
        "gpt-3.5-turbo-0301": 4032,
        "gpt-4-0314": 8092,
        "gpt-3.5-turbo": 4032,
        "gpt-4": 8092,
        "gpt-3.5-turbo-16k": 16184,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0314": 32768
    }
    return model_token_limit_dict


@patch.object(Models, "fetch_model_tokens", autospec=True)
def test_token_limit(mock_fetch_model_tokens, setup_model_token_limit):
    mock_fetch_model_tokens.return_value = setup_model_token_limit

    tc = TokenCounter(MagicMock(), 1)

    for model, expected_tokens in setup_model_token_limit.items():
        assert tc.token_limit(model) == expected_tokens

    assert tc.token_limit("non_existing_model") == 8092


def test_count_message_tokens():
    message_list = [{'content': 'Hello, How are you doing ?'}, {'content': 'I am good. How about you ?'}]
    BaseMessage.list_from_dicts = MagicMock(return_value=message_list)

    expected_token_count = TokenCounter.count_message_tokens(BaseMessage.list_from_dicts(message_list), "gpt-3.5-turbo-0301")
    assert expected_token_count == 26

    expected_token_count = TokenCounter.count_message_tokens(BaseMessage.list_from_dicts(message_list), "non_existing_model")
    assert expected_token_count == 26


def test_count_text_tokens():
    # You might need to adjust the hardcoded values in the TokenCounter.count_text_tokens function
    # and update the expected tokens accordingly if the function logic is changed.

    text = "You are a helpful assistant."
    assert TokenCounter.count_text_tokens(text) == 10

    text = "What is your name?"
    assert TokenCounter.count_text_tokens(text) == 9