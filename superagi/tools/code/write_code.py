import re
from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager


class CodingSchema(BaseModel):
    code_description: str = Field(
        ...,
        description="Description of the coding task",
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
        resource_manager: Manages the file resources
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "CodingTool"
    description = (
        "You will get instructions for code to write. You will write a very long answer. "
        "Make sure that every detail of the architecture is, in the end, implemented as code. "
        "Think step by step and reason yourself to the right decisions to make sure we get it right. "
        "You will first lay out the names of the core classes, functions, methods that will be necessary, "
        "as well as a quick comment on their purpose. Then you will output the content of each file including each function and class and ALL code."
    )
    args_schema: Type[CodingSchema] = CodingSchema
    goals: List[str] = []
    resource_manager: Optional[FileManager] = None
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, code_description: str) -> str:
        """
        Execute the write_code tool.

        Args:
            code_description : The coding task description.
            code_file_name: The name of the file where the generated codes will be saved.

        Returns:
            Generated code with where the code is being saved or error message.
        """
        prompt = PromptReader.read_tools_prompt(__file__, "write_code.txt") + "\nUseful to know:\n" + PromptReader.read_tools_prompt(__file__, "generate_logic.txt")
        prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
        prompt = prompt.replace("{code_description}", code_description)
        spec_response = self.tool_response_manager.get_last_response("WriteSpecTool")
        if spec_response != "":
            prompt = prompt.replace("{spec}", "Use this specs for generating the code:\n" + spec_response)
        logger.info(prompt)
        messages = [{"role": "system", "content": prompt}]

        total_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        token_limit = TokenCounter.token_limit(self.llm.get_model())
        result = self.llm.chat_completion(messages, max_tokens=(token_limit - total_tokens - 100))

        # Get all filenames and corresponding code blocks
        regex = r"(\S+?)\n```\S*\n(.+?)```"
        matches = re.finditer(regex, result["content"], re.DOTALL)

        file_names = []
        # Save each file

        for match in matches:
            # Get the filename
            file_name = re.sub(r'[<>"|?*]', "", match.group(1))
            if not file_name[0].isalnum():
                file_name = file_name[1:-1]

            # Get the code
            code = match.group(2)

            # Ensure file_name is not empty
            if not file_name.strip():
                continue

            file_names.append(file_name)
            save_result = self.resource_manager.write_file(file_name, code)
            if save_result.startswith("Error"):
                return save_result

        # Get README contents and save
        split_result = result["content"].split("```")
        if split_result:
            readme = split_result[0]
            save_readme_result = self.resource_manager.write_file("README.md", readme)
            if save_readme_result.startswith("Error"):
                return save_readme_result

        return result["content"] + "\n Codes generated and saved successfully in " + ", ".join(file_names)
