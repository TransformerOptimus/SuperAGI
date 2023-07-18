import json
import urllib
import boto3
import os
from superagi.config.config import get_config
from superagi.helper.resource_helper import ResourceHelper
from typing import Type, Optional
from pydantic import BaseModel, Field
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
import os
import requests
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager

class InstagramSchema(BaseModel):
    photo_description: str = Field(
        ...,
        description="description of the photo",
    )

class InstagramTool(BaseTool):
    """
    Instagram tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "Instagram tool"
    description = (
        "A tool performing posting AI generated photos on Instagram"
    )
    args_schema: Type[InstagramSchema] = InstagramSchema
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, photo_description: str) -> str:
        """
        Execute the Instagram tool.

        Args:
            photo_description : description of the photo to be posted

        Returns:
            Image posted successfully message if image has been posted on instagram or error message.
        """
        
        # Set your access token and photo URL
        print("***********************INSTA TOOL CALLED************************")
        import boto3
        s3 = boto3.client(
            's3',
            aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
        )
        last_tool_response = self.tool_response_manager.get_last_response()
        print('last_tool_response******************',last_tool_response)

        file_path="resources"+last_tool_response.partition("['")[2].partition("']")[0]
        print("**********file path********",file_path)

        response = s3.get_object(Bucket=get_config("BUCKET_NAME"), Key='output/car_dealership')
        content = response["Body"]

        print("***********content************",content)
        return "image posted successfully"

        meta_user_access_token = self.get_tool_config("META_USER_ACCESS_TOKEN")
        facebook_page_id=self.get_tool_config("FACEBOOK_PAGE_ID")

        if meta_user_access_token is None:
            return "Error: Missing meta user access token."

        if facebook_page_id is None:
            return "Error: Missing facebook page id."

        #create caption for the instagram
        caption=self.create_caption(photo_description)   
     
        response=requests.get(
            f"https://graph.facebook.com/v17.0/{facebook_page_id}?fields=instagram_business_account&access_token={meta_user_access_token}"
        )

        if response.status_code != 200:
            return f"Non-200 response: {str(response.text)}"

        data = response.json()
        insta_business_account_id=data["instagram_business_account"]["id"]

        
        bucket_name = get_config("INSTAGRAM_TOOL_BUCKET_NAME")
        output_root_dir = ResourceHelper.get_root_output_dir()

        for i in os.listdir(output_root_dir):
            # List files with .py
            if i.endswith(".jpeg") | i.endswith(".png"):
                object_key=i
        print("********object key",object_key)
        
        
        image_path=output_root_dir+object_key
        response=s3.upload_file(image_path, bucket_name, object_key)

        response = s3.list_objects_v2(
            Bucket=bucket_name,
        )
        
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

        encoded_caption=urllib. parse. quote(caption[1:-1])
        container_gen_url=f"https://graph.facebook.com/v17.0/{insta_business_account_id}/media?image_url={image_url}&caption={encoded_caption}&access_token={meta_user_access_token}"

        response = requests.post(
            container_gen_url
        )

        if response.status_code != 200:
            return f"Non-200 response: {str(response.text)}"

        data = response.json()
        container_ID=data["id"]
        response = requests.post(
            f"https://graph.facebook.com/v17.0/{insta_business_account_id}/media_publish?creation_id={container_ID}&access_token={meta_user_access_token}",
        )
        
        if response.status_code != 200:
            return f"Non-200 response: {str(response.text)}"
    
        return "Photo posted successfully!"
    
    def create_caption(self, photo_description: str) -> str:
        """
        Create a caption for the instagram post based on the photo description

        Args:
            photo_description : Description of the photo to be posted

        Returns:
            Description of the photo to be posted
        """
        caption_prompt ="""Generate an instagram post caption for the following text `{photo_description}`
            Write a concise as necessary and attempt to make it relevant to the description as best as possible. Add emojis if needed."""

        caption_prompt = caption_prompt.replace("{photo_description}", str(photo_description))

        messages = [{"role": "system", "content": caption_prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
        caption=result["content"]

        return caption