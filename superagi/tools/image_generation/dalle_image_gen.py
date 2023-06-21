from typing import Type, Optional

import requests
from pydantic import BaseModel, Field

from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.manager import ResourceManager
from superagi.tools.base_tool import BaseTool
from superagi.tools.image_generation.stable_diffusion_image_gen import StableDiffusionImageGenTool


class ImageGenInput(BaseModel):
    prompt: str = Field(..., description="Prompt for Image Generation to be used by Dalle.")
    size: int = Field(..., description="Size of the image to be Generated. default size is 512")
    num: int = Field(..., description="Number of Images to be generated. default num is 2")
    image_name: list = Field(..., description="Image Names for the generated images, example 'image_1.png'. Only include the image name. Don't include path.")


class ImageGenTool(BaseTool):
    """
    Dalle Image Generation tool

    Attributes:
        name : Name of the tool
        description : The description
        args_schema : The args schema
        llm : The llm
        agent_id : The agent id
        resource_manager : Manages the file resources
    """
    name: str = "DalleImageGeneration"
    args_schema: Type[BaseModel] = ImageGenInput
    description: str = "Generate Images using Dalle"
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    resource_manager: Optional[ResourceManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, prompt: str, image_name: list, size: int = 512, num: int = 2):
        """
        Execute the Dalle Image Generation tool.

        Args:
            prompt : The prompt for image generation.
            size : The size of the image to be generated.
            num : The number of images to be generated.
            image_name (list): The name of the image to be generated.

        Returns:
            Image generated successfully. or error message.
        """
        if size not in [256, 512, 1024]:
            size = min([256, 512, 1024], key=lambda x: abs(x - size))
        response = self.llm.generate_image(prompt, size, num)
        response = response.__dict__
        response = response['_previous']['data']
        for i in range(num):
            image = image_name[i]
            url = response[i]['url']
            data = requests.get(url).content
            self.resource_manager.write_binary_file(image, data)
        return "Images downloaded successfully"
