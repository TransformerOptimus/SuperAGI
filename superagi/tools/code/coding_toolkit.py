from abc import ABC
from typing import List

from superagi.tools.base_tool import BaseToolkit, BaseTool
from superagi.tools.code.write_code import CodingTool
from superagi.tools.code.write_spec import WriteSpecTool
from superagi.tools.code.write_test import WriteTestTool


class CodingToolkit(BaseToolkit, ABC):
    name: str = "CodingToolkit"
    description: str = "Coding Tool kit contains all tools related to coding tasks"

    def get_tools(self) -> List[BaseTool]:
        return [CodingTool(), WriteSpecTool(), WriteTestTool()]

    def get_env_keys(self) -> List[str]:
        return []
