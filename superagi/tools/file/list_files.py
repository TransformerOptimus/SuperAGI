import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool


class ListFileInput(BaseModel):
    """Input for CopyFileTool."""
    directory: str = Field(..., description="Directory to list files in")


class ListFileTool(BaseTool):
    name: str = "List File"
    args_schema: Type[BaseModel] = ListFileInput
    description: str = "lists files in a directory recursively"

    def _execute(self, directory: str):
        found_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith("."):
                    continue
                relative_path = os.path.join(root, file)
                found_files.append(relative_path)

        return found_files
