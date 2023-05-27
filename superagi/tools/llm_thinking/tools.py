from typing import Type

from pydantic import BaseModel, Field

from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool


class LlmTaskSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Text describing the task for which the LLM should generate a response.",
    )

class LlmThinkingTool(BaseTool):
    llm: BaseLlm = None
    name = "LlmThinkingTool"
    description = (
        "A tool that interacts with any given LLM "
        "to generate text given a certain task description."
    )
    args_schema: Type[LlmTaskSchema] = LlmTaskSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, task_description: str = "") -> str:
        try:
            messages = [{"role": "system", "content": task_description}]
            result = self.llm.chat_completion(messages)
            return result["content"]
        except Exception as e:
            print(e)
            return f"Error generating text: {e}"
