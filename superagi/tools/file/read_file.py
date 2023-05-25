import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config

import tweepy


class ReadFileSchema(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Path of the file to read")


class ReadFileTool(BaseTool):
    name: str = "Read File"
    args_schema: Type[BaseModel] = ReadFileSchema
    description: str = "Reads the file content in a specified location"

    def _execute(self, file_name: str):
        root_dir = get_config('RESOURCES_ROOT_DIR')
        final_path = file_name
        if root_dir is not None:
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + file_name
        else:
            final_path = os.getcwd() + "/" + file_name

        directory = os.path.dirname(final_path)
        os.makedirs(directory, exist_ok=True)

        file = open(final_path, 'r')
        file_content = file.read()
        return file_content
