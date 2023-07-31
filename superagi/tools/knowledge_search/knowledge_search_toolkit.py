from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.knowledge_search.knowledge_search import KnowledgeSearchTool
from superagi.models.tool_config import ToolConfig


class KnowledgeSearchToolkit(BaseToolkit, ABC):
    name: str = "Knowledge Search Toolkit"
    description: str = "Toolkit containing tools for performing search on the knowledge base."

    def get_tools(self) -> List[BaseTool]:
        return [KnowledgeSearchTool()]

    def get_env_keys(self) -> List[ToolConfig]:
        return []