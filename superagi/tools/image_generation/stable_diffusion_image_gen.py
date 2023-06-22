from typing import Type, Optional
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
import os
from PIL import Image
from io import BytesIO
import requests
import base64
from superagi.models.db import connect_db
from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from sqlalchemy.orm import sessionmaker
from superagi.lib.logger import logger


class StableDiffusionImageGenInput(BaseModel):
    prompt: str = Field(..., description="Prompt for Image Generation to be used by Stable Diffusion.")
    height: int = Field(..., description="Height of the image to be Generated. default height is 512")
    width: int = Field(..., description="Width of the image to be Generated. default width is 512")
    num: int = Field(..., description="Number of Images to be generated. default num is 2")
    steps: int = Field(..., description="Number of diffusion steps to run. default steps are 50")
    image_name: list = Field(...,
                             description="Image Names for the generated images, example 'image_1.png'. Only include the image name. Don't include path.")


class StableDiffusionImageGenTool(BaseTool):
    name: str = "Stable Diffusion Image Generation"
    args_schema: Type[BaseModel] = StableDiffusionImageGenInput
    description: str = "Generate Images using Stable Diffusion"
    agent_id: int = None

    def _execute(self, prompt: str, image_name: list, width: int = 512, height: int = 512, num: int = 2,
                 steps: int = 50):
        engine = connect_db()
        Session = sessionmaker(bind=engine)
        session = Session()

        api_key = get_config("STABILITY_API_KEY")

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

            image = image_name[i]
            root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')

            final_path = self.build_file_path(image, root_dir)

            try:
                self.upload_to_s3(final_img, final_path, image_format, image_name[i], session)

                logger.info(f"Image {image} saved successfully")
            except Exception as err:
                session.close()
                print(f"Error in _execute: {err}")
                return f"Error: {err}"
        session.close()
        return "Images downloaded and saved successfully"

    def call_stable_diffusion(self, api_key, width, height, num, prompt, steps):
        engine_id = get_config("ENGINE_ID")
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
                "text_prompts": [
                    {
                        "text": prompt
                    }
                ],
                "height": height,
                "width": width,
                "samples": num,
                "steps": steps,
            },
        )
        return response

    def upload_to_s3(self, final_img, final_path, image_format, file_name, session):
        with open(final_path, mode="wb") as img:
            final_img.save(img, format=image_format)
        with open(final_path, 'rb') as img:
            resource = ResourceHelper.make_written_file_resource(file_name=file_name,
                                                                 agent_id=self.agent_id, file=img, channel="OUTPUT")
            logger.info(resource)
            if resource is not None:
                session.add(resource)
                session.commit()
                session.flush()
                if resource.storage_type == "S3":
                    s3_helper = S3Helper()
                    s3_helper.upload_file(img, path=resource.path)

    def build_file_path(self, image, root_dir):
        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + image
        else:
            final_path = os.getcwd() + "/" + image
        return final_path
