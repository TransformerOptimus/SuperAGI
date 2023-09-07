import pytest
from unittest.mock import Mock

from superagi.llms.google_palm import GooglePalm
from superagi.llms.hugging_face import HuggingFace
from superagi.llms.llm_model_factory import get_model, build_model_with_api_key
from superagi.llms.openai import OpenAi
from superagi.llms.replicate import Replicate


# Fixtures for the mock objects
@pytest.fixture
def mock_openai():
    return Mock(spec=OpenAi)

@pytest.fixture
def mock_replicate():
    return Mock(spec=Replicate)

@pytest.fixture
def mock_google_palm():
    return Mock(spec=GooglePalm)

@pytest.fixture
def mock_hugging_face():
    return Mock(spec=HuggingFace)

@pytest.fixture
def mock_replicate():
    return Mock(spec=Replicate)

@pytest.fixture
def mock_google_palm():
    return Mock(spec=GooglePalm)

@pytest.fixture
def mock_hugging_face():
    return Mock(spec=HuggingFace)

# Test build_model_with_api_key function
def test_build_model_with_openai(mock_openai, monkeypatch):
    monkeypatch.setattr('superagi.llms.llm_model_factory.OpenAi', mock_openai)
    model = build_model_with_api_key('OpenAi', 'fake_key')
    mock_openai.assert_called_once_with(api_key='fake_key')
    assert isinstance(model, Mock)

def test_build_model_with_replicate(mock_replicate, monkeypatch):
    monkeypatch.setattr('superagi.llms.llm_model_factory.Replicate', mock_replicate)
    model = build_model_with_api_key('Replicate', 'fake_key')
    mock_replicate.assert_called_once_with(api_key='fake_key')
    assert isinstance(model, Mock)


def test_build_model_with_openai(mock_openai, monkeypatch):
    monkeypatch.setattr('superagi.llms.llm_model_factory.OpenAi', mock_openai)  # Replace 'your_module' with the actual module name
    model = build_model_with_api_key('OpenAi', 'fake_key')
    mock_openai.assert_called_once_with(api_key='fake_key')
    assert isinstance(model, Mock)

def test_build_model_with_replicate(mock_replicate, monkeypatch):
    monkeypatch.setattr('superagi.llms.llm_model_factory.Replicate', mock_replicate)  # Replace 'your_module' with the actual module name
    model = build_model_with_api_key('Replicate', 'fake_key')
    mock_replicate.assert_called_once_with(api_key='fake_key')
    assert isinstance(model, Mock)

def test_build_model_with_google_palm(mock_google_palm, monkeypatch):
    monkeypatch.setattr('superagi.llms.llm_model_factory.GooglePalm', mock_google_palm)  # Replace 'your_module' with the actual module name
    model = build_model_with_api_key('Google Palm', 'fake_key')
    mock_google_palm.assert_called_once_with(api_key='fake_key')
    assert isinstance(model, Mock)

def test_build_model_with_hugging_face(mock_hugging_face, monkeypatch):
    monkeypatch.setattr('superagi.llms.llm_model_factory.HuggingFace', mock_hugging_face)  # Replace 'your_module' with the actual module name
    model = build_model_with_api_key('Hugging Face', 'fake_key')
    mock_hugging_face.assert_called_once_with(api_key='fake_key')
    assert isinstance(model, Mock)

def test_build_model_with_unknown_provider(capsys):  # capsys is a built-in pytest fixture for capturing print output
    model = build_model_with_api_key('Unknown', 'fake_key')
    assert model is None
    captured = capsys.readouterr()
    assert "Unknown provider." in captured.out