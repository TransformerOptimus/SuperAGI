from abc import ABC
from typing import List

from superagi.tools.base_tool import BaseToolkit, BaseTool, ToolConfiguration
from superagi.tools.searx.searx import SearxSearchTool
from superagi.types.key_type import ToolConfigKeyType
import time
import requests

class SearxSearchTool:
    def search(self, query):
        url = "http://your-searx-instance/search"
        params = {
            'q': query,
            'format': 'json'
        }
        max_retries = 5
        backoff_factor = 1

        for attempt in range(max_retries):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                wait_time = backoff_factor * (2 ** attempt)
                print(f"Received 429 status code. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                response.raise_for_status()

        raise Exception("Max retries exceeded with 429 status code")

class SearxSearchToolkit(BaseToolkit, ABC):
    name: str = "Searx Toolkit"
    description: str = "Toolkit containing tools for performing Google search and extracting snippets and webpages " \
                       "using Searx"

    def get_tools(self) -> List[BaseTool]:
        return [SearxSearchTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return []
