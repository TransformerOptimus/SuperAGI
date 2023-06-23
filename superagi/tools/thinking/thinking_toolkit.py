from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.thinking.tools import ThinkingTool


class ThinkingToolkit(BaseToolkit, ABC):
    name: str = "Thinking Toolkit"
    description: str = "Toolkit containing tools for intelligent problem-solving"

    def get_tools(self) -> List[BaseTool]:
        return [
            ThinkingTool(),
        ]

    def get_env_keys(self) -> List[str]:
        return []
