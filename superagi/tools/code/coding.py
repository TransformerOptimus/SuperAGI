from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.lib.logger import logger


class CodingSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Coding task description.",
    )

class CodingTool(BaseTool):
    """
    Used to generate code.

    Attributes:
        llm: LLM used for code generation.
        name : The name of tool.
        description : The description of tool.
        args_schema : The args schema.
        goals : The goals.
    """
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
        """
        Execute the code tool.

        Args:
            task_description : The task description.

        Returns:
            Generated code or error message.
        """
        try:
            prompt = """You're a top-notch coder, knowing all programming languages, software systems, and architecture.
        
            Your high level goal is:
            {goals}
        
            Provide no information about who you are and focus on writing code.
            Ensure code is bug and error free and explain complex concepts through comments
            Respond in well-formatted markdown. Ensure code blocks are used for code sections.
        
            Write code to accomplish the following:
            {task}
            
            You will output the content of each file including ALL code. Each file will follow following mark down code block format:
            
            FILE_NAME: {file_name}
            ```{code_language}
            {code}
            ```
            
            You will start with the "entrypoint" file, then go to the ones that are imported by that file, and so on. 
            Please note that the code should be fully functional. No placeholders. Include module dependency or package manager dependency definition file.
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{task}", task_description)
            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            return result["content"]
        except Exception as e:
            logger.error(e)
            return f"Error generating text: {e}"