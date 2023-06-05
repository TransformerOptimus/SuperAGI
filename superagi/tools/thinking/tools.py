import os
import openai
from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from superagi.llms.base_llm import BaseLlm
from pydantic import BaseModel, Field, PrivateAttr


class ReasoningSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Task description which needs reasoning.",
    )

class ReasoningTool(BaseTool):
    llm: Optional[BaseLlm] = None
    name = "ReasoningTool"
    description = (
        "Intelligent problem-solving assistant that comprehends tasks, identifies key variables, and makes efficient decisions, all while providing detailed, self-driven reasoning for its choices."
        #"Enhances critical thinking and reasoning for diverse tasks, facilitating logical problem-solving in a streamlined manner"
    )
    args_schema: Type[ReasoningSchema] = ReasoningSchema
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True


    def _execute(self, task_description: str):
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
            print(e)
            return f"Error generating text: {e}"