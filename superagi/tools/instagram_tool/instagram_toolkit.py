from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.instagram_tool.instagram import InstagramTool
from superagi.types.key_type import ToolConfigKeyType

class InstagramToolkit(BaseToolkit, ABC):
    name: str = "Instagram Toolkit"
    description: str = "Toolkit containing tools for posting AI generated photo on Instagram. Posts only one photo in a run "

    def get_tools(self) -> List[BaseTool]:
        return [InstagramTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="META_USER_ACCESS_TOKEN", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=True),
            ToolConfiguration(key="FACEBOOK_PAGE_ID", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=False)
        ]