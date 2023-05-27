import os
import openai
from typing import Type

from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config

# Schema for LLMThinking tool

class LlmTaskSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Text describing the task for which the GPT model should generate a response.",
    )

class LlmThinkingTool(BaseTool):
    name = "LlmThinking"
    description = (
        "A tool that interacts with OpenAI's GPT models "
        "to generate text given a certain task description."
    )
    args_schema: Type[LlmTaskSchema] = LlmTaskSchema

    def _execute(self, task_description: str, model_name: str = "text-davinci-002"):
        api_key = get_config("OPENAI_API_KEY")
        openai.api_key = api_key

        try:
            response = openai.Completion.create(
                engine=model_name,
                prompt=task_description,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.7,
            )
            generated_text = response.choices[0].text.strip()
            return generated_text
        except openai.OpenAIError as e:
            print(e)
            return f"Error generating text: {e}"