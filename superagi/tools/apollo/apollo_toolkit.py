from abc import ABC
from typing import List

from superagi.tools.apollo.apollo_search import ApolloSearchTool
from superagi.tools.base_tool import BaseToolkit, BaseTool, ToolConfiguration
from superagi.types.key_type import ToolConfigKeyType


class ApolloToolkit(BaseToolkit, ABC):
    name: str = "ApolloToolkit"
    description: str = "Apollo Tool kit contains all tools related to apollo.io tasks"

    def get_tools(self) -> List[BaseTool]:
        return [ApolloSearchTool()]

    def get_env_keys(self) -> List[str]:
        return [ToolConfiguration(key="APOLLO_SEARCH_KEY", key_type=ToolConfigKeyType.STRING, is_required=True)]
