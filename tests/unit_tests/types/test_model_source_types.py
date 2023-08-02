import pytest

from superagi.types.model_source_types import ModelSourceType


def test_get_model_source_type():
    assert ModelSourceType.get_model_source_type('Google Palm') == ModelSourceType.GooglePalm
    assert ModelSourceType.get_model_source_type('OPENAI') == ModelSourceType.OpenAI

    with pytest.raises(ValueError) as excinfo:
        ModelSourceType.get_model_source_type('INVALIDSOURCE')
    assert "INVALIDSOURCE is not a valid vector store name." in str(excinfo.value)

def test_get_model_source_from_model():
    open_ai_models = ['gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4-32k']
    google_models = ['google-palm-bison-001', 'models/chat-bison-001']

    for model in open_ai_models:
        assert ModelSourceType.get_model_source_from_model(model) == ModelSourceType.OpenAI

    for model in google_models:
        assert ModelSourceType.get_model_source_from_model(model) == ModelSourceType.GooglePalm

    assert ModelSourceType.get_model_source_from_model('unregistered-model') == ModelSourceType.OpenAI

def test_str_representation():
    assert str(ModelSourceType.GooglePalm) == 'Google Palm'
    assert str(ModelSourceType.OpenAI) == 'OpenAi'
