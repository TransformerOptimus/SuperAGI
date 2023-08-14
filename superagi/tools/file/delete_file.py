import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent import Agent
from superagi.tools.base_tool import BaseTool
from superagi.types.storage_types import StorageType
from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper


class DeleteFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to delete")


class DeleteFileTool(BaseTool):
    """
    Delete File tool

    Attributes:
        name : The name.
        agent_id: The agent id.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Delete File"
    agent_id: int = None
    agent_execution_id:int = None
    args_schema: Type[BaseModel] = DeleteFileInput
    description: str = "Delete a file"

    def _execute(self, file_name: str):
        """
        Execute the delete file tool.

        Args:
            file_name : The name of the file to delete.

        Returns:
            success or error message.
        """
        final_path = ResourceHelper.get_agent_write_resource_path(file_name, Agent.get_agent_from_id(
            session=self.toolkit_config.session,
            agent_id=self.agent_id),
          AgentExecution.get_agent_execution_from_id(
              session=self.toolkit_config.session,
              agent_execution_id=self.agent_execution_id))
        
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
            try:
                S3Helper().delete_file(final_path)
                return "File deleted successfully."
            except Exception as err:
                return f"Error: {err}"
        else:
            try:
                os.remove(final_path)
                return "File deleted successfully."
            except Exception as err:
                return f"Error: {err}"