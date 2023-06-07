from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool


class CodingSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Coding task description.",
    )

class CodingTool(BaseTool):
    llm: Optional[BaseLlm] = None
    name = "CodingTool"
    description = (
        "Useful for writing, reviewing, and refactoring code. Can also fix bugs and explain programming concepts."
    )
    args_schema: Type[CodingSchema] = CodingSchema
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True


    def _execute(self, task_description: str):
        try:
            prompt = """You're a top-notch coder, knowing all programming languages, software systems, and architecture.
        
            Your high level goal is:
            {goals}
        
            Provide no information about who you are and focus on writing code.
            Ensure code is bug and error free and explain complex concepts through comments
            Respond in well-formatted markdown. Ensure code blocks are used for code sections.
        
            Write code to accomplish the following:
            {task}
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{task}", task_description)
            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            return result["content"]
        except Exception as e:
            print(e)
            return f"Error generating text: {e}"