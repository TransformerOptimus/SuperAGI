from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.resource.query_resource import QueryResourceTool
from superagi.models.tool_config import ToolConfig
from superagi.types.key_type import ToolConfigKeyType


class JiraToolkit(BaseToolkit, ABC):
    name: str = "Resource Toolkit"
    description: str = "Toolkit containing tools for Resource integration"

    def get_tools(self) -> List[BaseTool]:
        return [
            QueryResourceTool(),
        ]

    def get_env_keys(self) -> List[ToolConfig]:
        return [
            ToolConfig(key="RESOURCE_VECTOR_STORE", key_type=ToolConfigKeyType.STRING, is_required= True, is_secret = True),
            ToolConfig(key="RESOURCE_VECTOR_STORE_INDEX_NAME", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=True),
            ToolConfig(key="TEST_KEY_HELLO_1", key_type=ToolConfigKeyType.FILE, is_required = False, is_secret = False),
            ToolConfig(key="TEST_KEY_HELLO_2"),
            "TEST_KEY_HELLO_3"
            
        ]
