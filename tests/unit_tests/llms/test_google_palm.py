from unittest.mock import patch

from superagi.llms.google_palm import GooglePalm


@patch('superagi.llms.google_palm.palm')
def test_chat_completion(mock_palm):
    # Arrange
    model = 'models/text-bison-001'
    api_key = 'test_key'
    palm_instance = GooglePalm(api_key, model=model)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    max_tokens = 100
    mock_palm.generate_text.return_value.result = 'Sure, I can help with that.'

    # Act
    result = palm_instance.chat_completion(messages, max_tokens)

    # Assert
    assert result == {"response": mock_palm.generate_text.return_value, "content": 'Sure, I can help with that.'}
    mock_palm.generate_text.assert_called_once_with(
        model=model,
        prompt='You are a helpful assistant.',
        temperature=palm_instance.temperature,
        candidate_count=palm_instance.candidate_count,
        top_k=palm_instance.top_k,
        top_p=palm_instance.top_p,
        max_output_tokens=int(max_tokens)
    )


def test_verify_access_key():
    model = 'models/text-bison-001'
    api_key = 'test_key'
    palm_instance = GooglePalm(api_key, model=model)
    result = palm_instance.verify_access_key()
    assert result is False
