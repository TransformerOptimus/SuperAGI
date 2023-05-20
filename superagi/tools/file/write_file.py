import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool

import tweepy
from superagi.config.config import get_config


class WriteFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to write")
    content: str = Field(..., description="File content to write")


class WriteFileTool(BaseTool):
    name: str = "write_file"
    args_schema: Type[BaseModel] = WriteFileInput
    description: str = "Writes text to a file"

    def _execute(self, file_name: str, content: str):
        final_path = file_name
        root_dir = get_config('RESOURCES_ROOT_DIR')
        if root_dir is not None:
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + file_name
        else:
            final_path = os.getcwd() + "/" + file_name

        try:
            with open(final_path, 'w', encoding="utf-8") as file:
                file.write(content)
            return "File written to successfully."
        except Exception as err:
            return f"Error: {err}"
