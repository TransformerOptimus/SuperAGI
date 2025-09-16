"""
Tests for new AI provider integrations (Grok and Groq).
"""

import pytest
from unittest.mock import Mock, patch
from superagi.llms.grok import Grok
from superagi.llms.groq import Groq
from superagi.types.model_source_types import ModelSourceType


class TestGrokIntegration:
    """Test Grok (xAI) integration."""
    
    def test_grok_initialization(self):
        """Test Grok initialization."""
        with patch.dict('os.environ', {'XAI_API_KEY': 'test-key'}):
            grok = Grok(model="grok-beta")
            assert grok.model == "grok-beta"
            assert grok.api_key == "test-key"
    
    def test_grok_no_api_key(self):
        """Test Grok initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="xAI API key is required"):
                Grok()
    
    def test_grok_get_models(self):
        """Test getting available Grok models."""
        with patch.dict('os.environ', {'XAI_API_KEY': 'test-key'}):
            grok = Grok()
            models = grok.get_models()
            assert "grok-beta" in models
            assert "grok-1" in models
    
    def test_grok_token_limit(self):
        """Test Grok token limits."""
        with patch.dict('os.environ', {'XAI_API_KEY': 'test-key'}):
            grok = Grok(model="grok-beta")
            assert grok.get_token_limit() == 131072
    
    @patch('openai.OpenAI')
    def test_grok_chat_completion(self, mock_openai):
        """Test Grok chat completion."""
        # Mock the OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello from Grok!"
        mock_response.choices[0].message.role = "assistant"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'XAI_API_KEY': 'test-key'}):
            grok = Grok()
            response = grok.chat_completion([{"role": "user", "content": "Hello"}])
            
            assert response["choices"][0]["message"]["content"] == "Hello from Grok!"
            assert response["usage"]["total_tokens"] == 15


class TestGroqIntegration:
    """Test Groq (hardware-accelerated) integration."""
    
    def test_groq_initialization(self):
        """Test Groq initialization."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            groq = Groq(model="llama-3.1-70b-versatile")
            assert groq.model == "llama-3.1-70b-versatile"
            assert groq.api_key == "test-key"
    
    def test_groq_no_api_key(self):
        """Test Groq initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Groq API key is required"):
                Groq()
    
    def test_groq_get_models(self):
        """Test getting available Groq models."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            groq = Groq()
            models = groq.get_models()
            assert "llama-3.1-70b-versatile" in models
            assert "llama-3.1-8b-instant" in models
            assert "mixtral-8x7b-32768" in models
    
    def test_groq_token_limits(self):
        """Test Groq token limits for different models."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            groq_70b = Groq(model="llama-3.1-70b-versatile")
            assert groq_70b.get_token_limit() == 131072
            
            groq_mixtral = Groq(model="mixtral-8x7b-32768")
            assert groq_mixtral.get_token_limit() == 32768
    
    @patch('openai.OpenAI')
    def test_groq_chat_completion(self, mock_openai):
        """Test Groq chat completion."""
        # Mock the OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Ultra-fast response from Groq!"
        mock_response.choices[0].message.role = "assistant"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 8
        mock_response.usage.completion_tokens = 12
        mock_response.usage.total_tokens = 20
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            groq = Groq()
            response = groq.chat_completion([{"role": "user", "content": "Generate code"}])
            
            assert response["choices"][0]["message"]["content"] == "Ultra-fast response from Groq!"
            assert response["usage"]["total_tokens"] == 20
    
    def test_groq_inference_speed_info(self):
        """Test Groq inference speed information."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            groq = Groq()
            speed_info = groq.get_inference_speed()
            assert "hardware-accelerated" in speed_info.lower()
            assert "faster" in speed_info.lower()


class TestModelSourceTypes:
    """Test updated model source type detection."""
    
    def test_grok_model_detection(self):
        """Test Grok model detection."""
        assert ModelSourceType.get_model_source_from_model("grok-beta") == ModelSourceType.Grok
        assert ModelSourceType.get_model_source_from_model("grok-1") == ModelSourceType.Grok
    
    def test_groq_model_detection(self):
        """Test Groq model detection."""
        assert ModelSourceType.get_model_source_from_model("llama-3.1-70b-versatile") == ModelSourceType.Groq
        assert ModelSourceType.get_model_source_from_model("llama-3.1-8b-instant") == ModelSourceType.Groq
        assert ModelSourceType.get_model_source_from_model("mixtral-8x7b-32768") == ModelSourceType.Groq
    
    def test_existing_model_detection_still_works(self):
        """Test that existing model detection still works."""
        # OpenAI models
        assert ModelSourceType.get_model_source_from_model("gpt-4o") == ModelSourceType.OpenAI
        assert ModelSourceType.get_model_source_from_model("o1-preview") == ModelSourceType.OpenAI
        
        # Anthropic models
        assert ModelSourceType.get_model_source_from_model("claude-3-5-sonnet-20241022") == ModelSourceType.Anthropic
        
        # Google models
        assert ModelSourceType.get_model_source_from_model("gemini-1.5-pro") == ModelSourceType.GooglePalm
        
        # Replicate models
        assert ModelSourceType.get_model_source_from_model("meta/llama-2-70b-chat") == ModelSourceType.Replicate
    
    def test_enum_values(self):
        """Test that new enum values are correct."""
        assert ModelSourceType.Grok.value == "Grok"
        assert ModelSourceType.Groq.value == "Groq"
        assert ModelSourceType.Anthropic.value == "Anthropic"


class TestModelFactory:
    """Test LLM model factory with new providers."""
    
    @patch('superagi.llms.llm_model_factory.connect_db')
    @patch('superagi.llms.llm_model_factory.sessionmaker')
    def test_factory_grok_provider(self, mock_sessionmaker, mock_connect_db):
        """Test model factory with Grok provider."""
        # Mock database session and response
        mock_session = Mock()
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Mock model instance
        mock_model_instance = Mock()
        mock_model_instance.model_name = "grok-beta"
        mock_model_instance.version = "1.0"
        
        # Mock provider response
        mock_provider_response = Mock()
        mock_provider_response.provider = "Grok"
        
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_model_instance,  # First query for model instance
            mock_provider_response  # Second query for provider
        ]
        
        with patch.dict('os.environ', {'XAI_API_KEY': 'test-key'}):
            from superagi.llms.llm_model_factory import get_model
            
            with patch('superagi.llms.llm_model_factory.Grok') as mock_grok:
                mock_grok_instance = Mock()
                mock_grok.return_value = mock_grok_instance
                
                result = get_model(
                    organisation_id=1,
                    api_key="test-key",
                    model="grok-beta"
                )
                
                # Verify Grok was called with correct parameters
                mock_grok.assert_called_once_with(
                    model="grok-beta",
                    api_key="test-key"
                )
                assert result == mock_grok_instance
    
    @patch('superagi.llms.llm_model_factory.connect_db')
    @patch('superagi.llms.llm_model_factory.sessionmaker')
    def test_factory_groq_provider(self, mock_sessionmaker, mock_connect_db):
        """Test model factory with Groq provider."""
        # Mock database session and response
        mock_session = Mock()
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Mock model instance
        mock_model_instance = Mock()
        mock_model_instance.model_name = "llama-3.1-70b-versatile"
        mock_model_instance.version = "1.0"
        
        # Mock provider response
        mock_provider_response = Mock()
        mock_provider_response.provider = "Groq"
        
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_model_instance,  # First query for model instance
            mock_provider_response  # Second query for provider
        ]
        
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            from superagi.llms.llm_model_factory import get_model
            
            with patch('superagi.llms.llm_model_factory.Groq') as mock_groq:
                mock_groq_instance = Mock()
                mock_groq.return_value = mock_groq_instance
                
                result = get_model(
                    organisation_id=1,
                    api_key="test-key",
                    model="llama-3.1-70b-versatile"
                )
                
                # Verify Groq was called with correct parameters
                mock_groq.assert_called_once_with(
                    model="llama-3.1-70b-versatile",
                    api_key="test-key"
                )
                assert result == mock_groq_instance


if __name__ == "__main__":
    pytest.main([__file__])