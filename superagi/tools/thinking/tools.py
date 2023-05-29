import os
import openai
from typing import Type, Optional

from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from superagi.llms.base_llm import BaseLlm
from pydantic import BaseModel, Field, PrivateAttr


class LlmTaskSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Text describing the task for which the LLM should generate a response.",
    )

class LlmThinkingTool(BaseTool):
    llm: Optional[BaseLlm] = None
    name = "LlmThinkingTool"
    description = (
        "Tool enhances critical thinking and reasoning for diverse tasks, facilitating logical problem-solving in a streamlined manner"
    )
    args_schema: Type[LlmTaskSchema] = LlmTaskSchema

    class Config:
        arbitrary_types_allowed = True


    def _execute(self, task_description: str):
        try:
            messages = [{"role": "system", "content": task_description}]
            result = self.llm.chat_completion(messages)
            return result["content"]
        except Exception as e:
            print(e)
            return f"Error generating text: {e}"