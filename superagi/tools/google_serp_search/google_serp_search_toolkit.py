from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.google_serp_search.google_serp_search import GoogleSerpTool


class GoogleSerpToolkit(BaseToolkit, ABC):
    name: str = "Google SERP Toolkit"
    description: str = "Toolkit containing tools for performing Google SERP search and extracting snippets and webpages"

    def get_tools(self) -> List[BaseTool]:
        return [GoogleSerpTool()]

    def get_env_keys(self) -> List[str]:
        return [
            "SERP_API_KEY"
            # Add more config keys specific to your project
        ]
