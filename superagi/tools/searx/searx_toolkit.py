from abc import ABC
from typing import List

from superagi.tools.base_tool import BaseToolkit, BaseTool, ToolConfiguration
from superagi.tools.searx.searx import SearxSearchTool
from superagi.types.key_type import ToolConfigKeyType

class SearxSearchToolkit(BaseToolkit, ABC):
    name: str = "Searx Toolkit"
    description: str = "Toolkit containing tools for performing Google search and extracting snippets and webpages " \
                       "using Searx"

    def get_tools(self) -> List[BaseTool]:
        return [SearxSearchTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
