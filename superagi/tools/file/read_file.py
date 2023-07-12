import os
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent_execution import AgentExecution
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent


class ReadFileSchema(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Path of the file to read")


class ReadFileTool(BaseTool):
    """
    Read File tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Read File"
    agent_id: int = None
    agent_execution_id: int = None
    args_schema: Type[BaseModel] = ReadFileSchema
    description: str = "Reads the file content in a specified location"
    resource_manager: Optional[FileManager] = None

    def _execute(self, file_name: str):
        """
        Execute the read file tool.

        Args:
            file_name : The name of the file to read.

        Returns:
            The file content and the file name
        """
        final_path = ResourceHelper.get_agent_read_resource_path(file_name, agent=Agent.get_agent_from_id(
            session=self.toolkit_config.session, agent_id=self.agent_id), agent_execution=AgentExecution
                                                                 .get_agent_execution_from_id(session=self
                                                                                              .toolkit_config.session,
                                                                                              agent_execution_id=self
                                                                                              .agent_execution_id))
        if final_path is None or not os.path.exists(final_path):
            raise FileNotFoundError(f"File '{file_name}' not found.")

        directory = os.path.dirname(final_path)
        os.makedirs(directory, exist_ok=True)

        with open(final_path, 'r') as file:
            file_content = file.read()
        max_length = len(' '.join(file_content.split(" ")[:1000]))
        return file_content[:max_length] + "\n File " + file_name + " read successfully."


