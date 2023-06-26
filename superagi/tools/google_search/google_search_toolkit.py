from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.google_search.google_search import GoogleSearchTool


class GoogleSearchToolkit(BaseToolkit, ABC):
    name: str = "Google Search Toolkit"
    description: str = "Toolkit containing tools for performing Google search and extracting snippets and webpages"

    def get_tools(self) -> List[BaseTool]:
        return [GoogleSearchTool()]

    def get_env_keys(self) -> List[str]:
        return [
            "GOOGLE_API_KEY",
            "SEARCH_ENGINE_ID"
            # Add more config keys specific to your project
        ]
