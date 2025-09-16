import os
import openai
from typing import List, Dict, Any, Optional
from superagi.llms.base_llm import BaseLlm


class Groq(BaseLlm):
    def __init__(self, model: str = "llama-3.1-70b-versatile", api_key: Optional[str] = None, **kwargs):
        """
        Initialize Groq client for hardware-accelerated inference.
        
        Args:
            model: The model to use (default: "llama-3.1-70b-versatile")
            api_key: Groq API key
            **kwargs: Additional arguments passed to the base class
        """
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize Groq client (using OpenAI-compatible interface)
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        super().__init__(**kwargs)

    def get_models(self) -> List[str]:
        """Get available Groq models."""
        return [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant", 
            "llama-3-70b-8192",
            "llama-3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]

    def get_model(self) -> str:
        """Get current model name."""
        return self.model

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generate chat completion using Groq's hardware-accelerated inference.
        
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
            raise Exception(f"Groq API error: {str(e)}")

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text completion with ultra-fast inference.
        
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
            "llama-3.1-70b-versatile": 131072,
            "llama-3.1-8b-instant": 131072,
            "llama-3-70b-8192": 8192,
            "llama-3-8b-8192": 8192,
            "mixtral-8x7b-32768": 32768,
            "gemma-7b-it": 8192
        }
        return token_limits.get(self.model, 8192)

    def stream_chat_completion(self, messages: List[Dict[str, str]], **kwargs):
        """
        Stream chat completion responses with hardware acceleration.
        
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
            raise Exception(f"Groq streaming error: {str(e)}")

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

    def get_inference_speed(self) -> str:
        """
        Get information about Groq's inference speed advantage.
        
        Returns:
            Information about hardware acceleration
        """
        return "Groq provides hardware-accelerated inference with speeds up to 10x faster than traditional cloud providers"