import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.types.storage_types import StorageType
from superagi.config.config import get_config


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
        input_directory = ResourceHelper.get_root_input_dir()
        #output_directory = ResourceHelper.get_root_output_dir()
        if "{agent_id}" in input_directory:
            input_directory = ResourceHelper.get_formatted_agent_level_path(agent=Agent
                                                                            .get_agent_from_id(session=self
                                                                                               .toolkit_config.session,
                                                                                               agent_id=self.agent_id),
                                                                            path=input_directory)
        # if "{agent_id}" in output_directory:
        #     output_directory = output_directory.replace("{agent_id}", str(self.agent_id))
        input_files = self.list_files(input_directory)
        # output_files = self.list_files(output_directory)
        return input_files #+ output_files

    def list_files(self, directory):
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
            return S3Helper().list_files_from_s3(directory)
        found_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith(".") or "__pycache__" in root:
                    continue
                # relative_path = os.path.join(root, file)
                # input_directory = ResourceHelper.get_root_input_dir()
                # relative_path = relative_path.split(input_directory)[1]
                found_files.append(file)
        return found_files
