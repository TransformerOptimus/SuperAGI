from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.resource.query_resource import QueryResourceTool
from superagi.types.key_type import ToolConfigKeyType


class JiraToolkit(BaseToolkit, ABC):
    name: str = "Resource Toolkit"
    description: str = "Toolkit containing tools for Resource integration"

    def get_tools(self) -> List[BaseTool]:
        return [
            QueryResourceTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="RESOURCE_VECTOR_STORE", key_type=ToolConfigKeyType.STRING, is_required= True, is_secret = True),
            ToolConfiguration(key="RESOURCE_VECTOR_STORE_INDEX_NAME", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=True)
        ]
