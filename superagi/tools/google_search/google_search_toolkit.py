from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.google_search.google_search import GoogleSearchTool
from superagi.models.tool_config import ToolConfig
from superagi.types.key_type import ToolConfigKeyType


class GoogleSearchToolkit(BaseToolkit, ABC):
    name: str = "Google Search Toolkit"
    description: str = "Toolkit containing tools for performing Google search and extracting snippets and webpages"

    def get_tools(self) -> List[BaseTool]:
        return [GoogleSearchTool()]

    def get_env_keys(self) -> List[ToolConfig]:
        return [
            ToolConfig(key="GOOGLE_API_KEY", key_type=ToolConfigKeyType.STRING, is_required= True, is_secret = True),
            ToolConfig(key="SEARCH_ENGINE_ID", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=True)
        ]
