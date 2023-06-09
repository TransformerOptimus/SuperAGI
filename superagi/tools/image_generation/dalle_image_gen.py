from typing import Type, Optional
from pydantic import BaseModel, Field
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
import os
import requests
from superagi.models.db import connect_db
from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from sqlalchemy.orm import sessionmaker



class ImageGenInput(BaseModel):
    prompt: str = Field(..., description="Prompt for Image Generation to be used by Dalle.")
    size: int = Field(..., description="Size of the image to be Generated. default size is 512")
    num: int = Field(..., description="Number of Images to be generated. default num is 2")
    image_name: list = Field(..., description="Image Names for the generated images, example 'image_1.png'. Only include the image name. Don't include path.")


class ImageGenTool(BaseTool):
    name: str = "Dalle Image Generation"
    args_schema: Type[BaseModel] = ImageGenInput
    description: str = "Generate Images using Dalle"
    llm: Optional[BaseLlm] = None
    agent_id: int = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, prompt: str, image_name: list, size: int = 512, num: int = 2):
        engine = connect_db()
        Session = sessionmaker(bind=engine)
        session = Session()
        if size not in [256, 512, 1024]:
            size = min([256, 512, 1024], key=lambda x: abs(x - size))
        response = self.llm.generate_image(prompt, size, num)
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
                with open(final_path, 'rb') as img:
                    resource = ResourceHelper.make_written_file_resource(file_name=image_name[i],
                                                          agent_id=self.agent_id, file=img,channel="OUTPUT")
                    if resource is not None:
                        session.add(resource)
                        session.commit()
                        session.flush()
                        if resource.storage_type == "S3":
                            s3_helper = S3Helper()
                            s3_helper.upload_file(img, path=resource.path)
                    session.close()
                print(f"Image {image} saved successfully")
            except Exception as err:
                return f"Error: {err}"
        return "Images downloaded successfully"
