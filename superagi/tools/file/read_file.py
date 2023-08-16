
import os
from typing import Type, Optional
import ebooklib
import bs4 
from bs4 import BeautifulSoup

from pydantic import BaseModel, Field
from ebooklib import epub

from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from superagi.models.agent_execution import AgentExecution
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.types.storage_types import StorageType
from superagi.config.config import get_config
from unstructured.partition.auto import partition

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
    agent_id: int = None
    agent_execution_id: int = None
    args_schema: Type[BaseModel] = ReadFileSchema
    description: str = "Reads the file content in a specified location"
    resource_manager: Optional[FileManager] = None

    def _execute(self, file_name: str):
        """
        Execute the read file tool.

        Args:
            file_name : The name of the file to read.

        Returns:
            The file content and the file name
        """
        final_path = ResourceHelper.get_agent_read_resource_path(file_name, agent=Agent.get_agent_from_id(
            session=self.toolkit_config.session, agent_id=self.agent_id), agent_execution=AgentExecution
                                                                 .get_agent_execution_from_id(session=self
                                                                                              .toolkit_config.session,
                                                                                              agent_execution_id=self
                                                                                              .agent_execution_id))

        temporary_file_path = None
        final_name = final_path.split('/')[-1]
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
            if final_path.split('/')[-1].lower().endswith('.txt'):
                return S3Helper().read_from_s3(final_path)
            else:
                save_directory = "/"
                temporary_file_path = save_directory + file_name
                with open(temporary_file_path, "wb") as f:
                    contents = S3Helper().read_binary_from_s3(final_path)
                    f.write(contents)

        if final_path is None or not os.path.exists(final_path) and temporary_file_path is None:
            raise FileNotFoundError(f"File '{file_name}' not found.")
        directory = os.path.dirname(final_path)
        os.makedirs(directory, exist_ok=True)

        if temporary_file_path is not None:
            final_path = temporary_file_path

        
        # Check if the file is an .epub file
        if final_path.lower().endswith('.epub'):
            # Use ebooklib to read the epub file
            book = epub.read_epub(final_path)
            # Get the text content from each item in the book
            content = []
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                content.append(soup.get_text())

            content = "\n".join(content)
        else:
            elements = partition(final_path)
            content = "\n\n".join([str(el) for el in elements])

        if temporary_file_path is not None:
            os.remove(temporary_file_path)
   
        return content
    

