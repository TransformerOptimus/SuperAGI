import os
import openai
from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from superagi.llms.base_llm import BaseLlm
from pydantic import BaseModel, Field, PrivateAttr
from superagi.lib.logger import logger


class ThinkingSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Task description which needs reasoning.",
    )

class ThinkingTool(BaseTool):
    """
    Thinking tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        llm: LLM used for thinking.
    """
    llm: Optional[BaseLlm] = None
    name = "ThinkingTool"
    description = (
        "Intelligent problem-solving assistant that comprehends tasks, identifies key variables, and makes efficient decisions, all while providing detailed, self-driven reasoning for its choices."
    )
    args_schema: Type[ThinkingSchema] = ThinkingSchema
    goals: List[str] = []
    permission_required: bool = False

    class Config:
        arbitrary_types_allowed = True


    def _execute(self, task_description: str):
        """
        Execute the Thinking tool.

        Args:
            task_description : The task description.

        Returns:
            response from the Thinking tool. or error message.
        """
        try:
            prompt = """Given the following overall objective
            Objective:
            {goals} 
            
            and the following task, `{task_description}`.
            
            Perform the task by understanding the problem, extracting variables, and being smart
            and efficient. Provide a descriptive response, make decisions yourself when
            confronted with choices and provide reasoning for ideas / decisions.
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{task_description}", task_description)

            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            return result["content"]
        except Exception as e:
            logger.error(e)
            return f"Error generating text: {e}"