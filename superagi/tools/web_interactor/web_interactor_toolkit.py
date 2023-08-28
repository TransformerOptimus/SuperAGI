from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.web_interactor.web_interactor import WebInteractorTool
from superagi.models.tool_config import ToolConfig
from superagi.types.key_type import ToolConfigKeyType


class WebInteractorToolkit(BaseToolkit, ABC):
    name: str = "Web Interactor Toolkit"
    description: str = "Toolkit containing tools for interacting with web pages and performing actions like button click, typing and web page navigation"

    def get_tools(self) -> List[BaseTool]:
        return [WebInteractorTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
        ]