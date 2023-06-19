from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool


class CreateSpecSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Coding task description.",
    )


class CodingTool(BaseTool):
    llm: Optional[BaseLlm] = None
    name = "CreateSpecTool"
    description = (
        "Step-by-step guide for developers to create comprehensive, clear, and detailed specifications for new programming tasks/projects"
    )
    args_schema: Type[CreateSpecSchema] = CreateSpecSchema
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, task_description: str):
        try:
            prompt = """
            As an expert developer, you're tasked with creating a detailed plan for a new program.

            Your high level goal is:
            {goals}
            
            Write detail plan to accomplish the following task:
            {task}
            
            Firstly, clearly describe what the program will do and its key features. Make sure to clarify any possible uncertainties.
            
            Secondly, list and describe the main classes, functions, and methods that will be needed.
            
            Finally, note down any non-standard dependencies you'll need.
            
            This plan will guide the program's implementation later on.

            You're a top-notch coder, knowing all programming languages, software systems, and architecture.
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{task}", task_description)
            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            return result["content"]
        except Exception as e:
            print(e)
            return f"Error generating text: {e}"