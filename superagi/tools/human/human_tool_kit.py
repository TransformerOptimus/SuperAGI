from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolKit
from superagi.tools.human.tool import HumanInput


class HumanInputToolKit(BaseToolKit, ABC):
    name: str = "Human Input Toolkit"
    description: str = "Toolkit containing a tool for asking a human for guidance"

    def get_tools(self) -> List[BaseTool]:
        return [HumanInput()]

    def get_env_keys(self) -> List[str]:
        return []
