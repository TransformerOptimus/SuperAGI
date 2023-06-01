import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config



class DeleteFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to delete")

class DeleteFileTool(BaseTool):
    name: str = "Delete File"
    args_schema: Type[BaseModel] = DeleteFileInput
    description: str = "Delete a file"
    file_server_type: str = "s3"

    def _execute(self, file_name: str, content: str):
        final_path = file_name
        root_dir = get_config('RESOURCES_INPUT_ROOT_DIR')
        if root_dir is not None:
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + file_name
        else:
            final_path = os.getcwd() + "/" + file_name
        try:
            os.remove(final_path)
            return "File deleted successfully."
        except Exception as err:
            return f"Error: {err}"
