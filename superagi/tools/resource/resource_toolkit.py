from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.resource.query_resource import QueryResourceTool


class JiraToolkit(BaseToolkit, ABC):
    name: str = "Resource Toolkit"
    description: str = "Toolkit containing tools for Resource integration"

    def get_tools(self) -> List[BaseTool]:
        return [
            QueryResourceTool(),
        ]

    def get_env_keys(self) -> List[str]:
        return [
            "RESOURCE_VECTOR_STORE",
            "RESOURCE_VECTOR_STORE_INDEX_NAME",
        ]
