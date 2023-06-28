import os
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.resource_manager.manager import ResourceManager
from superagi.tools.base_tool import BaseTool


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
    args_schema: Type[BaseModel] = ReadFileSchema
    description: str = "Reads the file content in a specified location"
    resource_manager: Optional[ResourceManager] = None

    def _execute(self, file_name: str):
        """
        Execute the read file tool.

        Args:
            file_name : The name of the file to read.

        Returns:
            The file content and the file name
        """
        output_root_dir = ResourceHelper.get_root_output_dir()

        final_path = ResourceHelper.get_root_input_dir() + file_name
        if "{agent_id}" in final_path:
            final_path = final_path.replace("{agent_id}", str(self.agent_id))

        if final_path is None or not os.path.exists(final_path):
            if output_root_dir is not None:
                final_path = ResourceHelper.get_root_output_dir() + file_name
                if "{agent_id}" in final_path:
                    final_path = final_path.replace("{agent_id}", str(self.agent_id))

        if final_path is None or not os.path.exists(final_path):
            raise FileNotFoundError(f"File '{file_name}' not found.")

        directory = os.path.dirname(final_path)
        os.makedirs(directory, exist_ok=True)

        with open(final_path, 'r') as file:
            file_content = file.read()
        max_length = len(' '.join(file_content.split(" ")[:1000]))
        return file_content[:max_length] + "\n File " + file_name + " read successfully."


