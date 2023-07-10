from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.knowledge_tool.knowledge import KnowledgeSearchTool


class KnowledgeSearchToolkit(BaseToolkit, ABC):
    name: str = "Knowledge Search Toolkit"
    description: str = "Toolkit containing tools for performing search on the knowledge base."

    def get_tools(self) -> List[BaseTool]:
        return [KnowledgeSearchTool()]

    def get_env_keys(self) -> List[str]:
        return [
            "KNOWLEDGE_BASE",
            "KNOWLEDGE_API_KEY",
            "KNOWLEDGE_INDEX_OR_COLLECTION",
            "KNOWLEDGE_URL",
            "KNOWLEDGE_ENVIRONMENT"
            # Add more config keys specific to your project
        ]
