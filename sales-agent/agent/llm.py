import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.config import config


class LLM:
    """Language Model interface for agent decision making"""

    def __init__(self, model: str = None):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = model or config.DEFAULT_MODEL

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Get chat completion from LLM

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with response content and tool calls
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)

            result = {
                "content": response.choices[0].message.content or "",
                "tool_calls": [],
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }

            # Extract tool calls if present
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    })

            return result

        except Exception as e:
            print(f"LLM Error: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": [],
                "tokens_used": 0,
                "error": str(e)
            }

    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text from a prompt

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        messages = [{"role": "user", "content": prompt}]
        result = self.chat_completion(messages, temperature=temperature, max_tokens=max_tokens)
        return result.get("content", "")
