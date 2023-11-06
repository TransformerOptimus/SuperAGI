import pytest
from unittest.mock import MagicMock, patch
from superagi.llms.openai import OpenAi


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


def test_verify_access_key():
    model = 'gpt-4'
    api_key = 'test_key'
    openai_instance = OpenAi(api_key, model=model)
    result = openai_instance.verify_access_key()
    assert result is False
