from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolKit
from superagi.tools.image_generation.dalle_image_gen import ImageGenTool


class ImageGenToolKit(BaseToolKit, ABC):
    name: str = "Image Generation Toolkit"
    description: str = "Toolkit containing a tool for generating images using Dalle"

    def get_tools(self) -> List[BaseTool]:
        return [ImageGenTool()]

    def get_env_keys(self) -> List[str]:
        return ["RESOURCES_OUTPUT_ROOT_DIR"]
