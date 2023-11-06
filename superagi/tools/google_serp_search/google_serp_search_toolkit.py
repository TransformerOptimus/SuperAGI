from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.google_serp_search.google_serp_search import GoogleSerpTool
from superagi.models.tool_config import ToolConfig
from superagi.types.key_type import ToolConfigKeyType

class GoogleSerpToolkit(BaseToolkit, ABC):
    name: str = "Google SERP Toolkit"
    description: str = "Toolkit containing tools for performing Google SERP search and extracting snippets and webpages"

    def get_tools(self) -> List[BaseTool]:
        return [GoogleSerpTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="SERP_API_KEY", key_type=ToolConfigKeyType.STRING, is_required= True, is_secret = True)
        ]
