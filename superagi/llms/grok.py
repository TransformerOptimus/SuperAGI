import os
import openai
from typing import List, Dict, Any, Optional
from superagi.llms.base_llm import BaseLlm


class Grok(BaseLlm):
    def __init__(self, model: str = "grok-beta", api_key: Optional[str] = None, **kwargs):
        """
        Initialize Grok client.
        
        Args:
            model: The Grok model to use (default: "grok-beta")
            api_key: xAI API key
            **kwargs: Additional arguments passed to the base class
        """
        self.model = model
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("xAI API key is required. Set XAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize xAI client (using OpenAI-compatible interface)
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
        
        super().__init__(**kwargs)

    def get_models(self) -> List[str]:
        """Get available Grok models."""
        return ["grok-beta", "grok-1"]

    def get_model(self) -> str:
        """Get current model name."""
        return self.model

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generate chat completion using Grok.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional arguments (temperature, max_tokens, etc.)
            
        Returns:
            Dict containing the response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            
            return {
                "choices": [
                    {
                        "message": {
                            "content": response.choices[0].message.content,
                            "role": response.choices[0].message.role
                        },
                        "finish_reason": response.choices[0].finish_reason
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            }
            
        except Exception as e:
            raise Exception(f"Grok API error: {str(e)}")

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional arguments
            
        Returns:
            Generated text
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, **kwargs)
        return response["choices"][0]["message"]["content"]

    def get_token_limit(self) -> int:
        """Get token limit for the model."""
        token_limits = {
            "grok-beta": 131072,
            "grok-1": 131072
        }
        return token_limits.get(self.model, 131072)

    def stream_chat_completion(self, messages: List[Dict[str, str]], **kwargs):
        """
        Stream chat completion responses.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional arguments
            
        Yields:
            Streaming response chunks
        """
        try:
            kwargs["stream"] = True
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield {
                        "choices": [
                            {
                                "delta": {
                                    "content": chunk.choices[0].delta.content
                                }
                            }
                        ]
                    }
                    
        except Exception as e:
            raise Exception(f"Grok streaming error: {str(e)}")

    def verify_access_key(self) -> bool:
        """
        Verify that the API key is valid.
        
        Returns:
            True if the API key is valid, False otherwise
        """
        try:
            # Test with a simple completion
            self.generate_text("Hello", max_tokens=1)
            return True
        except:
            return False