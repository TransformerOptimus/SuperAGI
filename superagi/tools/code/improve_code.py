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


class ImproveCodeSchema(BaseModel):
    pass
    # code_data: str = Field(
    #     ...,
    #     description="Data generated previously by CodingTool",
    # )
class ImproveCodeTool(BaseTool):
    """
    Used to improve the already generated code.

    Attributes:
        llm: LLM used for code generation.
        name : The name of the tool.
        description : The description of the tool.
        resource_manager: Manages the file resources.
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "ImproveCodeTool"
    description = (
        "This tool improves the generated code."
    )
    resource_manager: Optional[FileManager] = None
    tool_response_manager: Optional[ToolResponseQueryManager] = None
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True

    def _execute(self) -> str:
        """
        Execute the improve code tool.

        Returns:
            Improved code or error message.
        """
        # Get all file names that the CodingTool has written
        file_names = self.resource_manager.get_files()

        # Loop through each file
        for file_name in file_names:
            print("#############################$$$$$$$$$$$$$$$$$$$$$@")
            # Read the file content
            content = self.resource_manager.read_file(file_name)

            # Generate a prompt from improve_code.txt
            prompt = PromptReader.read_tools_prompt(__file__, "improve_code.txt")

            # Combine the hint from the file, goals, and content
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{content}", content)

            # Add the file content to the chat completion prompt
            prompt = prompt + "\nOriginal Code:\n```\n" + content + "\n```"

            # Use LLM to generate improved code
            result = self.llm.chat_completion([{'role': 'system', 'content': prompt}])
            improved_content = result["messages"][0]["content"]

            # Rewrite the file with the improved content
            save_result = self.resource_manager.write_file(file_name, improved_content)

            if save_result.startswith("Error"):
                return save_result

        return f"All codes improved and saved successfully in: " + " ".join(file_names)