import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config


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
    args_schema: Type[BaseModel] = ReadFileSchema
    description: str = "Reads the file content in a specified location"

    def _execute(self, file_name: str):
        """
        Execute the read file tool.

        Args:
            file_name : The name of the file to read.

        Returns:
            The file content
        """
        input_root_dir = get_config('RESOURCES_INPUT_ROOT_DIR')
        output_root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
        final_path = None

        if input_root_dir is not None:
            input_root_dir = input_root_dir if input_root_dir.startswith("/") else os.getcwd() + "/" + input_root_dir
            input_root_dir = input_root_dir if input_root_dir.endswith("/") else input_root_dir + "/"
            final_path = input_root_dir + file_name

        if final_path is None or not os.path.exists(final_path):
            if output_root_dir is not None:
                output_root_dir = output_root_dir if output_root_dir.startswith(
                    "/") else os.getcwd() + "/" + output_root_dir
                output_root_dir = output_root_dir if output_root_dir.endswith("/") else output_root_dir + "/"
                final_path = output_root_dir + file_name

        if final_path is None or not os.path.exists(final_path):
            raise FileNotFoundError(f"File '{file_name}' not found.")

        directory = os.path.dirname(final_path)
        os.makedirs(directory, exist_ok=True)

        with open(final_path, 'r') as file:
            file_content = file.read()
        return file_content[:1500]
