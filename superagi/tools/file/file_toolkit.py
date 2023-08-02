from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.file.append_file import AppendFileTool
from superagi.tools.file.delete_file import DeleteFileTool
from superagi.tools.file.list_files import ListFileTool
from superagi.tools.file.read_file import ReadFileTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.types.key_type import ToolConfigKeyType
from superagi.models.tool_config import ToolConfig


class FileToolkit(BaseToolkit, ABC):
    name: str = "File Toolkit"
    description: str = "File Tool kit contains all tools related to file operations"

    def get_tools(self) -> List[BaseTool]:
        return [AppendFileTool(), DeleteFileTool(), ListFileTool(), ReadFileTool(), WriteFileTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
