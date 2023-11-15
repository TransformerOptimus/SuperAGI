"""Toolkit for interacting with the YeagerAI tools."""
from __future__ import annotations

from typing import List

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool


class YeagerAIToolkit:
    """Toolkit for interacting with a JSON spec."""

    def __init__(self) -> None:
        self.tools_list: List[BaseTool] = []

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return self.tools_list

    def register_tool(self, tool: BaseTool):
        """Register a tool to the toolkit."""
        self.tools_list.append(tool)
