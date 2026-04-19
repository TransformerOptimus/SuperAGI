from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class BaseLlm(ABC):
    """Abstract base class for LLM integrations
    
    Defines the interface for different LLM providers (OpenAI, Google Palm, etc.)
    """
    
    @abstractmethod
    def chat_completion(self, prompt: str, **kwargs) -> str:
        """Get chat completion from the LLM
        
        Args:
            prompt: The input prompt for the LLM
            **kwargs: Additional parameters like temperature, max_tokens, etc.
            
        Returns:
            str: The LLM's response text
        """
        pass

    @abstractmethod
    def get_source(self) -> str:
        """Get the source/provider name
        
        Returns:
            str: Name of the LLM provider (e.g., 'openai', 'google_palm')
        """
        pass

    @abstractmethod
    def get_api_key(self) -> str:
        """Get the API key for this LLM
        
        Returns:
            str: The API key
        """
        pass

    @abstractmethod
    def get_model(self) -> str:
        """Get the current model name
        
        Returns:
            str: The model identifier
        """
        pass

    @abstractmethod
    def get_models(self) -> List[str]:
        """Get list of available models
        
        Returns:
            List[str]: List of available model names
        """
        pass

    @abstractmethod
    def verify_access_key(self) -> bool:
        """Verify that the API key is valid
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        pass
    
    def get_token_limit(self) -> Optional[int]:
        """Get the token limit for the current model
        
        Returns:
            Optional[int]: Maximum tokens allowed, None if not available
        """
        return None
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for input text
        
        Args:
            text: The text to count tokens for
            
        Returns:
            int: Estimated number of tokens
        """
        # Simple estimation: ~4 chars per token on average
        return len(text) // 4
