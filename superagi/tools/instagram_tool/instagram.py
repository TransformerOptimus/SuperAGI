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
        "A tool for posting an AI generated photo on Instagram"
    )
    args_schema: Type[InstagramSchema] = InstagramSchema
    tool_response_manager: Optional[ToolResponseQueryManager] = None
    agent_id:int =None
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
        file_path=self.get_file_path_from_image_generation_tool()     
        #handling case where image generation generates multiple images
        if(file_path=="resources"):
            return "A photo has already been posted on your instagram account. To post multiple photos use recurring runs."
        
        image_url,encoded_caption=self.get_img_url_and_encoded_caption(photo_description,file_path)
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

    def get_image_from_s3(self,s3,file_path):
        """
        Gets the image from the s3 bucket

        Args:
            s3: S3 client
            file_path: path of the image file in s3

        Returns
            The image file from s3
        """
        
        response = s3.get_object(Bucket=get_config("BUCKET_NAME"), Key=file_path)
        content = response["Body"].read()

        return content

    def get_file_path_from_image_generation_tool(self):
        """
        Parses the output of the previous tool (Stable diffusion) and returns the path of the image file

        Args:

        Returns:
            The path of the image file generated by the image generation toolkit
        """
        
        last_tool_response = self.tool_response_manager.get_last_response()
        file_path="resources"+last_tool_response.partition("['")[2].partition("']")[0]
    
        if ',' in file_path:
            # Split the string based on the comma and get the first element (substring before the comma)
            file_path = file_path.split(',')[0].strip()
            file_path=file_path[:-1]

        return file_path

    def create_s3_client(self):
        """
        Creates an s3 client

        Args:

        Returns:
            The s3 client
        """
        
        s3 = boto3.client(
            's3',
            aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
        )

        return s3
        
    def get_img_public_url(self,s3,file_path,content):
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
        object_key=f"instagram_upload_images/{file_path.split('/')[-1]}{random.randint(0, 1000)}"
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=content)
        
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        return image_url

    def get_img_url_and_encoded_caption(self,photo_description,file_path):
        #creating an s3 client
        s3 = self.create_s3_client()    

        #fetching the image from the s3 using the file_path
        content = self.get_image_from_s3(s3,file_path)      

        #storing the image in a public bucket and getting the image url
        image_url = self.get_img_public_url(s3,file_path,content)       
        #encoding the caption with possible emojis and hashtags and removing the starting and ending double quotes 
        encoded_caption=self.create_caption(photo_description)    

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
