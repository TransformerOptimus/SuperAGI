from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class BaseTool(ABC):
    """Base class for all tools"""

    name: str
    description: str
    args_schema: type[BaseModel]

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments"""
        pass

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def to_llm_format(self) -> Dict[str, Any]:
        """Convert tool to LLM function calling format"""
        schema = self.args_schema.model_json_schema()

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", [])
                }
            }
        }
