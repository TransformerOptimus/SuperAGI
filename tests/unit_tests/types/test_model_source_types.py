import pytest

from superagi.types.model_source_types import ModelSourceType


def test_get_model_source_type():
    assert ModelSourceType.get_model_source_type('Google Palm') == ModelSourceType.GooglePalm
    assert ModelSourceType.get_model_source_type('OPENAI') == ModelSourceType.OpenAI
    assert ModelSourceType.get_model_source_type('ANTHROPIC') == ModelSourceType.Anthropic

    with pytest.raises(ValueError) as excinfo:
        ModelSourceType.get_model_source_type('INVALIDSOURCE')
    assert "INVALIDSOURCE is not a valid vector store name." in str(excinfo.value)

def test_get_model_source_from_model():
    # Updated to test latest OpenAI models
    open_ai_models = [
        # GPT-4 models
        'gpt-4', 'gpt-4-32k', 'gpt-4-0125-preview', 'gpt-4-1106-preview',
        'gpt-4-turbo', 'gpt-4-turbo-2024-04-09', 'gpt-4-turbo-preview', 
        'gpt-4o', 'gpt-4o-2024-08-06', 'gpt-4o-mini', 'gpt-4o-mini-2024-07-18',
        # New reasoning models
        'o1-preview', 'o1-mini',
        # GPT-3.5 models
        'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-0125', 
        'gpt-3.5-turbo-1106', 'gpt-3.5-turbo-instruct'
    ]
    # Updated to test latest Google models
    google_models = [
        # Latest Gemini models
        'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro', 
        'gemini-pro', 'gemini-pro-vision',
        'models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-1.0-pro',
        'models/gemini-pro', 'models/gemini-pro-vision',
        # Legacy PaLM models
        'google-palm-bison-001', 'models/chat-bison-001', 'models/text-bison-001'
    ]
    # Updated Replicate models
    replicate_models = [
        # Latest LLaMA models
        'meta/llama-2-70b-chat', 'meta/llama-2-13b-chat', 'meta/llama-2-7b-chat',
        'meta/codellama-70b-instruct', 'meta/codellama-34b-instruct', 'meta/codellama-13b-instruct',
        # Legacy model identifiers
        'replicate-llama13b-v2-chat', 'llama-2-70b-chat', 'llama-2-13b-chat', 'llama-2-7b-chat',
        'codellama-34b-instruct', 'codellama-13b-instruct'
    ]
    # Updated Anthropic models with latest releases
    anthropic_models = [
        # Claude 3.5 series (latest)
        'claude-3-5-sonnet-20241022', 'claude-3-5-sonnet-20240620', 'claude-3-5-haiku-20241022',
        # Claude 3 series
        'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307',
        # Claude 2 series (legacy)
        'claude-2.1', 'claude-2.0', 'claude-instant-1.2'
    ]

    for model in open_ai_models:
        assert ModelSourceType.get_model_source_from_model(model) == ModelSourceType.OpenAI

    for model in google_models:
        assert ModelSourceType.get_model_source_from_model(model) == ModelSourceType.GooglePalm

    for model in replicate_models:
        assert ModelSourceType.get_model_source_from_model(model) == ModelSourceType.Replicate

    for model in anthropic_models:
        assert ModelSourceType.get_model_source_from_model(model) == ModelSourceType.Anthropic

    assert ModelSourceType.get_model_source_from_model('unregistered-model') == ModelSourceType.OpenAI

def test_str_representation():
    assert str(ModelSourceType.GooglePalm) == 'Google Palm'
    assert str(ModelSourceType.OpenAI) == 'OpenAi'
    assert str(ModelSourceType.Anthropic) == 'Anthropic'
