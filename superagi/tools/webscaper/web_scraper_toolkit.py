from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.webscaper.tools import WebScraperTool


class WebScrapperToolkit(BaseToolkit, ABC):
    name: str = "Web Scraper Toolkit"
    description: str = "Web Scraper toolkit is used to scrape the web"

    def get_tools(self) -> List[BaseTool]:
        return [
            WebScraperTool(),
        ]

    def get_env_keys(self) -> List[str]:
        return []
