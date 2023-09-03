import re
import subprocess
from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.lib.logger import logger
from superagi.helper.resource_helper import ResourceHelper
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager


class RunCodeSchema(BaseModel):
    file_name: str = Field(
        ...,
        description="Name of the code file to run"
    )


class RunCodeTool(BaseTool):
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    agent_execution_id: int = None
    name = "RunCodeTool"
    description = "This tool can be used to run python code."
    args_schema: Type[RunCodeSchema] = RunCodeSchema
    goals: List[str] = []
    resource_manager: Optional[FileManager] = None
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, file_name: str) -> str:
        final_path = ResourceHelper.get_agent_read_resource_path(
            file_name, agent=Agent.get_agent_from_id(session=self.toolkit_config.session, agent_id=self.agent_id),
            agent_execution=AgentExecution.
            get_agent_execution_from_id(session=self.toolkit_config.session,agent_execution_id=self.agent_execution_id))

        result = subprocess.run(["python", final_path], capture_output=True, text=True)
        if result.returncode != 0:
            # Error occurred
            return f"An error occurred while running the script:\n\n{result.stderr}"
        else:
            return f"Result of running {file_name} : {result.stdout}"
        # Run the python code
