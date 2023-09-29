import os
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent_execution import AgentExecution
from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.types.storage_types import StorageType
from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper
from superagi.resource_manager.file_manager import FileManager

class AppendFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to write")
    content: str = Field(..., description="The text to append to the file")


class AppendFileTool(BaseTool):
    """
    Append File tool

    Attributes:
        name : The name.
        agent_id: The agent id.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Append File"
    agent_id: int = None
    agent_execution_id: int = None
    args_schema: Type[BaseModel] = AppendFileInput
    description: str = "Append text to a file"
    resource_manager: Optional[FileManager] = None

    def _execute(self, file_name: str, content: str):
        """
        Execute the append file tool.

        Args:
            file_name : The name of the file to write.
            content : The text to append to the file.

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
            previous_content = self.get_previous_content(final_path)
            if previous_content is None:
                return "Append file only supported for .txt Files."
            if not previous_content:
                return "File not Found."
            S3Helper().delete_file(final_path)
            new_content = previous_content + content
            return self.resource_manager.write_file(file_name, new_content)

        try:
            directory = os.path.dirname(final_path)
            os.makedirs(directory, exist_ok=True)
            with open(final_path, 'a+', encoding="utf-8") as file:
                file.write(content)
            return "File written to successfully."
        except Exception as err:
            return f"Error: {err}"
    
    def get_previous_content(self, final_path):
        if final_path.split('/')[-1].lower().endswith('.txt'):
            try:
                return S3Helper().read_from_s3(final_path)
            except Exception:
                return False