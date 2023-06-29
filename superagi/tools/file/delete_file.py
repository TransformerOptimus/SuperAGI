import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.tools.base_tool import BaseTool


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
        final_path = ResourceHelper.get_root_output_dir()
        if "{agent_id}" in final_path:
            final_path = final_path.replace("{agent_id}", str(self.agent_id))
        try:
            os.remove(final_path + file_name)
            return "File deleted successfully."
        except Exception as err:
            return f"Error: {err}"
