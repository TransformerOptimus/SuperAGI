from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.lib.logger import logger


class WriteTestSchema(BaseModel):
    spec_description: str = Field(
        ...,
        description="Specification for generating tests.",
    )


class WriteTestTool(BaseTool):
    """
    Used to generate pytest unit tests based on the specification.

    Attributes:
        llm: LLM used for test generation.
        name : The name of tool.
        description : The description of tool.
        args_schema : The args schema.
        goals : The goals.
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "WriteTestTool"
    description = (
        "You are a super smart developer using Test Driven Development to write tests according to a specification.\n"
        "Please generate tests based on the above specification. The tests should be as simple as possible, "
        "but still cover all the functionality.\n"
        "Write it in the file"
    )
    args_schema: Type[WriteTestSchema] = WriteTestSchema
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, spec_description: str) -> str:
        """
        Execute the write_test tool.

        Args:
            spec_description : The specification description.

        Returns:
            Generated pytest unit tests or error message.
        """
        try:
            prompt = """You are a super smart developer who practices Test Driven Development for writing tests according to a specification.

            Your high-level goal is:
            {goals}

            Please generate pytest unit tests based on the following specification description:
            {spec}

            The tests should be as simple as possible, but still cover all the functionality described in the specification.
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{spec}", spec_description)
            messages = [{"role": "system", "content": prompt}]

            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            return result["content"]

        except Exception as e:
            logger.error(e)
            return f"Error generating tests: {e}"