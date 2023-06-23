import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config



class DeleteFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to delete")

class DeleteFileTool(BaseTool):
    """
    Delete File tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Delete File"
    args_schema: Type[BaseModel] = DeleteFileInput
    description: str = "Delete a file"

    def _execute(self, file_name: str, content: str):
        """
        Execute the delete file tool.

        Args:
            file_name : The name of the file to delete.
            content : The text to append to the file.

        Returns:
            file deleted successfully. or error message.
        """
        final_path = ResourceHelper.get_resource_path(file_name)
        try:
            os.remove(final_path)
            return "File deleted successfully."
        except Exception as err:
            return f"Error: {err}"
