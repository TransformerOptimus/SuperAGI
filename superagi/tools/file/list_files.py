import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.tools.base_tool import BaseTool


class ListFileInput(BaseModel):
    pass


class ListFileTool(BaseTool):
    """
    List File tool

    Attributes:
        name : The name.
        agent_id: The agent id.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "List File"
    agent_id: int = None
    args_schema: Type[BaseModel] = ListFileInput
    description: str = "lists files in a directory recursively"

    def _execute(self):
        """
        Execute the list file tool.

        Args:
            directory : The directory to list files in.

        Returns:
            list of files in directory.
        """
        input_files = self.list_files(ResourceHelper.get_root_input_dir() + str(self.agent_id) + "/")
        output_files = self.list_files(ResourceHelper.get_root_output_dir() + str(self.agent_id) + "/")
        return input_files + output_files

    def list_files(self, directory):
        found_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith("."):
                    continue
                relative_path = os.path.join(root, file)
                found_files.append(relative_path)
        return found_files
