from unittest.mock import MagicMock, patch

from superagi.llms.llm_model_factory import ModelFactory, factory, get_model


def test_model_factory():
    # Arrange
    mock_factory = ModelFactory()
    mock_factory._creators = {
        "gpt-4": MagicMock(side_effect=lambda **kwargs: "OpenAI GPT-4 mock"),
        "gpt-3.5-turbo": MagicMock(side_effect=lambda **kwargs: "OpenAI GPT-3.5-turbo mock"),
        "google-palm-bison-001": MagicMock(side_effect=lambda **kwargs: "Google Palm Bison mock")
    }

    # Act
    gpt_4_model = mock_factory.get_model("gpt-4", api_key="test_key")
    gpt_3_5_turbo_model = mock_factory.get_model("gpt-3.5-turbo", api_key="test_key")
    google_palm_model = mock_factory.get_model("google-palm-bison-001", api_key="test_key")

    # Assert
    assert gpt_4_model == "OpenAI GPT-4 mock"
    assert gpt_3_5_turbo_model == "OpenAI GPT-3.5-turbo mock"
    assert google_palm_model == "Google Palm Bison mock"


def test_get_model():
    # Arrange
    api_key = "test_key"
    model = "gpt-3.5-turbo"

    with patch.object(factory, 'get_model', return_value="OpenAI GPT-3.5-turbo mock") as mock_method:
        # Act
        result = get_model(api_key, model)

        # Assert
        assert result == "OpenAI GPT-3.5-turbo mock"
        mock_method.assert_called_once_with(model, api_key=api_key)
