import os
from typing import Type
from pydantic import BaseModel, Field

from superagi.resource_manager.manager import ResourceManager
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.helper.resource_helper import ResourceHelper
# from superagi.helper.s3_helper import upload_to_s3
from superagi.helper.s3_helper import S3Helper
from superagi.lib.logger import logger




class WriteFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to write. Only include the file name. Don't include path.")
    content: str = Field(..., description="File content to write")


class WriteFileTool(BaseTool):
    """
    Write File tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Write File"
    args_schema: Type[BaseModel] = WriteFileInput
    description: str = "Writes text to a file"
    agent_id: int = None
    resource_manager: ResourceManager = None

    def _execute(self, file_name: str, content: str):
        """
        Execute the write file tool.

        Args:
            file_name : The name of the file to write.
            content : The text to write to the file.

        Returns:
            file written to successfully. or error message.
        """
        self.resource_manager.write_file(file_name, content)

