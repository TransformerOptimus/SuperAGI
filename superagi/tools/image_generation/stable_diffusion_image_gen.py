import base64
from io import BytesIO
from typing import Type, Optional

import requests
from PIL import Image
from pydantic import BaseModel, Field
from superagi.helper.resource_helper import ResourceHelper
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent import Agent


class StableDiffusionImageGenInput(BaseModel):
    prompt: str = Field(..., description="Prompt for Image Generation to be used by Stable Diffusion. The prompt should be as descriptive as possible and mention all the details of the image to be generated")
    height: int = Field(..., description="Height of the image to be Generated. default height is 512")
    width: int = Field(..., description="Width of the image to be Generated. default width is 512")
    num: int = Field(..., description="Number of Images to be generated. default num is 2")
    steps: int = Field(..., description="Number of diffusion steps to run. default steps are 50")
    image_names: list = Field(...,
                              description="Image Names for the generated images, example 'image_1.png'. Only include the image name. Don't include path.")


class StableDiffusionImageGenTool(BaseTool):
    """
        Stable diffusion Image Generation tool

        Attributes:
            name : Name of the tool
            description : The description
            args_schema : The args schema
            agent_id : The agent id
            resource_manager : Manages the file resources
        """
    name: str = "Stable Diffusion Image Generation"
    args_schema: Type[BaseModel] = StableDiffusionImageGenInput
    description: str = "Generate Images using Stable Diffusion"
    agent_id: int = None
    agent_execution_id: int = None
    resource_manager: Optional[FileManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, prompt: str, image_names: list, width: int = 512, height: int = 512, num: int = 2,
                 steps: int = 50):
        api_key = self.get_tool_config("STABILITY_API_KEY")

        if api_key is None:
            return "Error: Missing Stability API key."
        response = self.call_stable_diffusion(api_key, width, height, num, prompt, steps)

        if response.status_code != 200:
            return f"Non-200 response: {str(response.text)}"

        data = response.json()

        artifacts = data['artifacts']
        base64_strings = []
        for artifact in artifacts:
            base64_strings.append(artifact['base64'])

        for i in range(num):
            image_base64 = base64_strings[i]
            img_data = base64.b64decode(image_base64)
            final_img = Image.open(BytesIO(img_data))
            image_format = final_img.format
            img_byte_arr = BytesIO()
            final_img.save(img_byte_arr, format=image_format)

            self.resource_manager.write_binary_file(image_names[i], img_byte_arr.getvalue())

        return f"Images downloaded and saved successfully!!"

    def call_stable_diffusion(self, api_key, width, height, num, prompt, steps):
        engine_id = self.get_tool_config("ENGINE_ID")
        if "768" in engine_id:
            if height < 768:
                height = 768
            if width < 768:
                width = 768
        response = requests.post(
            f"https://api.stability.ai/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "text_prompts": [{"text": prompt}],
                "height": height,
                "width": width,
                "samples": num,
                "steps": steps,
            },
        )
        return response
