import openai
import pytest
from unittest.mock import MagicMock, patch

from superagi.llms.openai import OpenAi, MAX_RETRY_ATTEMPTS


@patch('superagi.llms.openai.openai')
def test_chat_completion(mock_openai):
    # Arrange
    model = 'gpt-4'
    api_key = 'test_key'
    openai_instance = OpenAi(api_key, model=model)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    max_tokens = 100
    mock_chat_response = MagicMock()
    mock_chat_response.choices[0].message = {"content": "I'm here to help!"}
    mock_openai.ChatCompletion.create.return_value = mock_chat_response

    # Act
    result = openai_instance.chat_completion(messages, max_tokens)

    # Assert
    assert result == {"response": mock_chat_response, "content": "I'm here to help!"}
    mock_openai.ChatCompletion.create.assert_called_once_with(
        n=openai_instance.number_of_results,
        model=model,
        messages=messages,
        temperature=openai_instance.temperature,
        max_tokens=max_tokens,
        top_p=openai_instance.top_p,
        frequency_penalty=openai_instance.frequency_penalty,
        presence_penalty=openai_instance.presence_penalty
    )


@patch('superagi.llms.openai.wait_random_exponential.__call__')
@patch('superagi.llms.openai.openai')
def test_chat_completion_retry_rate_limit_error(mock_openai, mock_wait_random_exponential):
    # Arrange
    model = 'gpt-4'
    api_key = 'test_key'
    openai_instance = OpenAi(api_key, model=model)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    max_tokens = 100

    mock_openai.ChatCompletion.create.side_effect = openai.error.RateLimitError("Rate limit exceeded")

    # Mock sleep time
    mock_wait_random_exponential.return_value = 0.1

    # Act
    result = openai_instance.chat_completion(messages, max_tokens)

    # Assert
    assert result == {"error": "ERROR_OPENAI", "message": "Open ai exception: Rate limit exceeded"}
    assert mock_openai.ChatCompletion.create.call_count == MAX_RETRY_ATTEMPTS


@patch('superagi.llms.openai.wait_random_exponential.__call__')
@patch('superagi.llms.openai.openai')
def test_chat_completion_retry_timeout_error(mock_openai, mock_wait_random_exponential):
    # Arrange
    model = 'gpt-4'
    api_key = 'test_key'
    openai_instance = OpenAi(api_key, model=model)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    max_tokens = 100

    mock_openai.ChatCompletion.create.side_effect = openai.error.Timeout("Timeout occured")

    # Mock sleep time
    mock_wait_random_exponential.return_value = 0.1

    # Act
    result = openai_instance.chat_completion(messages, max_tokens)

    # Assert
    assert result == {"error": "ERROR_OPENAI", "message": "Open ai exception: Timeout occured"}
    assert mock_openai.ChatCompletion.create.call_count == MAX_RETRY_ATTEMPTS


@patch('superagi.llms.openai.wait_random_exponential.__call__')
@patch('superagi.llms.openai.openai')
def test_chat_completion_retry_try_again_error(mock_openai, mock_wait_random_exponential):
    # Arrange
    model = 'gpt-4'
    api_key = 'test_key'
    openai_instance = OpenAi(api_key, model=model)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    max_tokens = 100

    mock_openai.ChatCompletion.create.side_effect = openai.error.TryAgain("Try Again")

    # Mock sleep time
    mock_wait_random_exponential.return_value = 0.1

    # Act
    result = openai_instance.chat_completion(messages, max_tokens)

    # Assert
    assert result == {"error": "ERROR_OPENAI", "message": "Open ai exception: Try Again"}
    assert mock_openai.ChatCompletion.create.call_count == MAX_RETRY_ATTEMPTS


def test_verify_access_key():
    model = 'gpt-4'
    api_key = 'test_key'
    openai_instance = OpenAi(api_key, model=model)
    result = openai_instance.verify_access_key()
    assert result is False
