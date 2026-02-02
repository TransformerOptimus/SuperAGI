from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.bocha_search.bocha_search import BoChaTool
from superagi.models.tool_config import ToolConfig
from superagi.types.key_type import ToolConfigKeyType

class BoChaToolkit(BaseToolkit, ABC):
    name: str = "BoCha Toolkit"
    description: str = "Toolkit containing tools for performing BoCha search and extracting snippets and webpages"

    def get_tools(self) -> List[BaseTool]:
        return [BoChaTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="BoCha_API_KEY", key_type=ToolConfigKeyType.STRING, is_required= True, is_secret = True)
        ]