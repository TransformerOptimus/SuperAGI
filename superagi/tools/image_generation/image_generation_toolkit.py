from abc import ABC
from typing import List

from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.image_generation.dalle_image_gen import DalleImageGenTool
from superagi.tools.image_generation.stable_diffusion_image_gen import StableDiffusionImageGenTool


class ImageGenToolkit(BaseToolkit, ABC):
    name: str = "Image Generation Toolkit"
    description: str = "Toolkit containing a tool for generating images"

    def get_tools(self) -> List[BaseTool]:
        return [DalleImageGenTool(), StableDiffusionImageGenTool()]

    def get_env_keys(self) -> List[str]:
        return ["STABILITY_API_KEY", "ENGINE_ID"]
