from typing import Type
from pydantic import BaseModel, Field
from superagi.helper.token_counter import TokenCounter
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
import os
import openai
import requests

class ImageGenInput(BaseModel):
    prompt: str = Field(..., description="Prompt for Image Generation to be used by Dalle.")
    size: int = Field(..., description="Size of the image to be Generated.")
    num: int = Field(..., description="Number of Images to be generated")
    image_name: list = Field(..., description="Image Names for the generated images")

class ImageGenTool(BaseTool):
    name: str = "Dalle Image Generation"
    args_schema: Type[BaseModel] = ImageGenInput
    description: str = "Generate Images using Dalle"

    def _execute(self, prompt: str, image_name: list, size: int = 512, num: int = 2):
        if size not in [256,512,1024]:
            size= min([256,512,1024], key=lambda x: abs(x-size))
        openai.api_key = get_config('OPENAI_API_KEY')
        response = openai.Image.create(
            prompt = prompt,
            n = num,
            size = f"{size}x{size}"
        )
        response = response.__dict__
        response = response['_previous']['data']
        for i in range(num):
            image = image_name[i]
            final_path = image
            root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
            if root_dir is not None:
                root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
                root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
                final_path = root_dir + image
            else:
                final_path = os.getcwd() + "/" + image
            url = response[i]['url']
            data = requests.get(url).content
            try:
                with open(final_path, mode="wb") as img:
                    img.write(data)
                print(f"Image {image} saved successfully")
            except Exception as err:
                return f"Error: {err}"
        return "Images downloaded successfully"