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
import random
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.helper.s3_helper import S3Helper
from superagi.types.storage_types import StorageType

class InstagramSchema(BaseModel):
    photo_description: str = Field(
        ...,
        description="description of the photo",
    )
    filename: str = Field(..., description="Name of the file to be posted. Only one file can be posted at a time.")


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
        "A tool for posting an AI generated photo on Instagram"
    )
    args_schema: Type[InstagramSchema] = InstagramSchema
    tool_response_manager: Optional[ToolResponseQueryManager] = None
    agent_id:int =None
    agent_execution_id:int =None
    
    class Config:
        arbitrary_types_allowed = True

    def _execute(self, photo_description: str, filename: str) -> str:
        """
        Execute the Instagram tool.

        Args:
            photo_description : description of the photo to be posted

        Returns:
            Image posted successfully message if image has been posted on instagram or error message.
        """
        session = self.toolkit_config.session
        meta_user_access_token = self.get_tool_config("META_USER_ACCESS_TOKEN")
        facebook_page_id=self.get_tool_config("FACEBOOK_PAGE_ID")

        if meta_user_access_token is None:
            return "Error: Missing meta user access token."

        if facebook_page_id is None:
            return "Error: Missing facebook page id."
        #create caption for the instagram
        caption=self.create_caption(photo_description)   

        #get request for fetching the instagram_business_account_id
        root_api_url="https://graph.facebook.com/v17.0/"
        response=self.get_req_insta_id(root_api_url,facebook_page_id,meta_user_access_token)
        
        if response.status_code != 200:
            return f"Non-200 response: {str(response.text)}"

        data = response.json()
        insta_business_account_id=data["instagram_business_account"]["id"]
        file_path=self.get_file_path(session, filename, self.agent_id, self.agent_execution_id)    
        #handling case where image generation generates multiple images
        
        image_url,encoded_caption=self.get_img_url_and_encoded_caption(photo_description,file_path, filename)
        #post request for getting the media container ID
        response=self.post_media_container_id(root_api_url,insta_business_account_id,image_url,encoded_caption,meta_user_access_token)
        
        if response.status_code != 200:
            return f"Non-200 response: {str(response.text)}"

        data = response.json()
        container_ID=data["id"]
        #post request to post the media container on instagram account
        response=self.post_media(root_api_url,insta_business_account_id,container_ID,meta_user_access_token)
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
            Attempt to make it as relevant as possible to the description and should be different and unique everytime. Add relevant emojis and hashtags."""

        caption_prompt = caption_prompt.replace("{photo_description}", str(photo_description))

        messages = [{"role": "system", "content": caption_prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
        caption=result["content"]
        
        encoded_caption=urllib. parse. quote(caption)     

        return encoded_caption
    
    def get_file_path(self, session, file_name, agent_id, agent_execution_id):
        """
        Gets the path of the image file

        Args:
            media_files: Name of the media files to be posted

        Returns:
            The path of the image file
        """
        
        final_path = ResourceHelper().get_agent_read_resource_path(file_name,
                                                                    agent=Agent.get_agent_from_id(session, agent_id),
                                                                    agent_execution=AgentExecution.get_agent_execution_from_id(
                                                                  session, agent_execution_id))
        return final_path
        
    def get_img_public_url(self,filename,content):
        """
        Puts the image generated by image generation tool in the s3 bucket and returns the public url of the same
        Args:
            s3 : S3 bucket
            file_path: Path of the image file in s3
            content: Image file

        Returns:
            The public url of the image put in s3 bucket
        """
        
        bucket_name = get_config("INSTAGRAM_TOOL_BUCKET_NAME")
        object_key=f"instagram_upload_images/{filename}"
        S3Helper(get_config("INSTAGRAM_TOOL_BUCKET_NAME")).upload_file_content(content, object_key)
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        return image_url

    def get_img_url_and_encoded_caption(self,photo_description,file_path,filename):

        #fetching the image from the s3 using the file_path
        content = self._get_image_content(file_path)
        #storing the image in a public bucket and getting the image url
        image_url = self.get_img_public_url(filename,content)       
        #encoding the caption with possible emojis and hashtags and removing the starting and ending double quotes 
        encoded_caption=self.create_caption(photo_description)    

        print(image_url, encoded_caption)

        return image_url,encoded_caption

    def get_req_insta_id(self,root_api_url,facebook_page_id,meta_user_access_token):
        url_to_get_acc_id=f"{root_api_url}{facebook_page_id}?fields=instagram_business_account&access_token={meta_user_access_token}"
        response=requests.get(
            url_to_get_acc_id
        )

        return response
    
    def post_media_container_id(self,root_api_url,insta_business_account_id,image_url,encoded_caption,meta_user_access_token):
        url_to_create_media_container=f"{root_api_url}{insta_business_account_id}/media?image_url={image_url}&caption={encoded_caption}&access_token={meta_user_access_token}"
        response = requests.post(       
            url_to_create_media_container
        )

        return response

    def post_media(self,root_api_url,insta_business_account_id,container_ID,meta_user_access_token):
        url_to_post_media_container=f"{root_api_url}{insta_business_account_id}/media_publish?creation_id={container_ID}&access_token={meta_user_access_token}"
        response = requests.post(
            url_to_post_media_container
        )

        return response

    def _get_image_content(self, file_path):
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
                attachment_data = S3Helper().read_binary_from_s3(file_path)
        else:
            with open(file_path, "rb") as file:
                attachment_data = file.read()
        return attachment_data