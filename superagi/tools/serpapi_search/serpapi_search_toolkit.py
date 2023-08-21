from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.serpapi_search.serpapi import SerpApiSearchTool
from superagi.models.tool_config import ToolConfig
from superagi.types.key_type import ToolConfigKeyType


class SerpApiSearchToolkit(BaseToolkit, ABC):
    name: str = "SerpApi Search Toolkit"
    description: str = "Toolkit containing tools for performing Google/Bing/Yahoo!/Baidu/DuckDuckGo/Yandex/Naver/... search and extracting snippets and webpages"

    def get_tools(self) -> List[BaseTool]:
        return [SerpApiSearchTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(
                key="SERPAPI_API_KEY",
                key_type=ToolConfigKeyType.STRING,
                is_required=True,
                is_secret=True,
            ),
            ToolConfiguration(
                key="SERPAPI_ENGINE",
                key_type=ToolConfigKeyType.STRING,
                is_required=False,
                is_secret=False,
            ),
            ToolConfiguration(
                key="SERPAPI_NO_CACHE",
                key_type=ToolConfigKeyType.STRING,
                is_required=False,
                is_secret=False,
            ),
        ]
