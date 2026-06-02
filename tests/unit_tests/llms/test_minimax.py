import pytest
from unittest.mock import MagicMock, patch

from superagi.llms.minimax import MiniMax, MAX_RETRY_ATTEMPTS, MINIMAX_API_BASE


def test_get_source():
    minimax = MiniMax(api_key='test_key')
    assert minimax.get_source() == "minimax"


def test_get_api_key():
    minimax = MiniMax(api_key='test_key')
    assert minimax.get_api_key() == 'test_key'


def test_get_model_default():
    minimax = MiniMax(api_key='test_key')
    assert minimax.get_model() == 'MiniMax-M3'


def test_get_model_custom():
    minimax = MiniMax(api_key='test_key', model='MiniMax-M2.7-highspeed')
    assert minimax.get_model() == 'MiniMax-M2.7-highspeed'


def test_get_models():
    minimax = MiniMax(api_key='test_key')
    models = minimax.get_models()
    assert 'MiniMax-M3' in models
    assert 'MiniMax-M2.7' in models
    assert 'MiniMax-M2.7-highspeed' in models
    # M3 should appear first (as the default)
    assert models.index('MiniMax-M3') < models.index('MiniMax-M2.7')
    # Older models should be removed
    assert 'MiniMax-M2.5' not in models
    assert 'MiniMax-M2.5-highspeed' not in models
    assert 'MiniMax-M2.1' not in models
    assert 'MiniMax-M2' not in models
    assert 'MiniMax-M1' not in models


def test_temperature_clamping():
    # Temperature=0 should be clamped to 0.01
    minimax = MiniMax(api_key='test_key', temperature=0)
    assert minimax.temperature == 0.01

    # Negative temperature should be clamped to 0.01
    minimax = MiniMax(api_key='test_key', temperature=-0.5)
    assert minimax.temperature == 0.01

    # Positive temperature should pass through
    minimax = MiniMax(api_key='test_key', temperature=0.7)
    assert minimax.temperature == 0.7


@patch('superagi.llms.minimax.openai')
def test_chat_completion(mock_openai):
    model = 'MiniMax-M3'
    api_key = 'test_key'
    minimax_instance = MiniMax(api_key, model=model)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    max_tokens = 100
    mock_chat_response = MagicMock()
    mock_chat_response.choices[0].message = {"content": "Hello from MiniMax!"}
    mock_openai.ChatCompletion.create.return_value = mock_chat_response

    result = minimax_instance.chat_completion(messages, max_tokens)

    assert result == {"response": mock_chat_response, "content": "Hello from MiniMax!"}
    mock_openai.ChatCompletion.create.assert_called_once_with(
        n=minimax_instance.number_of_results,
        model=model,
        messages=messages,
        temperature=minimax_instance.temperature,
        max_tokens=max_tokens,
        top_p=minimax_instance.top_p,
        frequency_penalty=minimax_instance.frequency_penalty,
        presence_penalty=minimax_instance.presence_penalty
    )


@patch('superagi.llms.minimax.openai')
def test_chat_completion_sets_api_base(mock_openai):
    minimax_instance = MiniMax(api_key='test_key')
    mock_chat_response = MagicMock()
    mock_chat_response.choices[0].message = {"content": "test"}
    mock_openai.ChatCompletion.create.return_value = mock_chat_response

    minimax_instance.chat_completion([{"role": "user", "content": "hi"}], 100)

    # Verify the API base was set to MiniMax endpoint
    assert mock_openai.api_base == MINIMAX_API_BASE
    assert mock_openai.api_key == 'test_key'


@patch('superagi.llms.minimax.openai')
def test_chat_completion_authentication_error(mock_openai):
    import openai
    minimax_instance = MiniMax(api_key='bad_key')
    mock_openai.ChatCompletion.create.side_effect = openai.error.AuthenticationError("Invalid API key")

    result = minimax_instance.chat_completion([{"role": "user", "content": "hi"}], 100)

    assert result["error"] == "ERROR_AUTHENTICATION"
    assert "Authentication error" in result["message"]


@patch('superagi.llms.minimax.openai')
def test_chat_completion_generic_exception(mock_openai):
    minimax_instance = MiniMax(api_key='test_key')
    mock_openai.ChatCompletion.create.side_effect = Exception("Something went wrong")

    result = minimax_instance.chat_completion([{"role": "user", "content": "hi"}], 100)

    assert result["error"] == "ERROR_MINIMAX"
    assert "MiniMax exception" in result["message"]


@patch('superagi.llms.minimax.openai')
def test_verify_access_key_success(mock_openai):
    minimax = MiniMax(api_key='valid_key')
    mock_openai.ChatCompletion.create.return_value = MagicMock()
    result = minimax.verify_access_key()
    assert result is True


@patch('superagi.llms.minimax.openai')
def test_verify_access_key_failure(mock_openai):
    import openai
    minimax = MiniMax(api_key='bad_key')
    mock_openai.ChatCompletion.create.side_effect = openai.error.AuthenticationError("Invalid key")
    result = minimax.verify_access_key()
    assert result is False
