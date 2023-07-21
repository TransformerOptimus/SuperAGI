from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.instagram_tool.instagram import InstagramTool
from superagi.tools.image_generation.stable_diffusion_image_gen import StableDiffusionImageGenTool

class InstagramToolkit(BaseToolkit, ABC):
    name: str = "Instagram Toolkit"
    description: str = "Toolkit containing tools for posting AI generated photo on Instagram. Posts only one photo in a run "

    def get_tools(self) -> List[BaseTool]:
        return [InstagramTool(),StableDiffusionImageGenTool()]

    def get_env_keys(self) -> List[str]:
        return [
            "META_USER_ACCESS_TOKEN",
            "FACEBOOK_PAGE_ID"
            # Add more config keys specific to your project
        ]