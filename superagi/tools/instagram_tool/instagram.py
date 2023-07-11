import json
from typing import Type, Optional

from pydantic import BaseModel, Field
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from instabot import Bot
import os
import glob
import requests

class InstagramSchema(BaseModel):
    caption: str = Field(
        ...,
        description="Caption for the photo",
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
        "A tool performing posting jpeg on Instagram"
    )
    args_schema: Type[InstagramSchema] = InstagramSchema

    class Config:
        arbitrary_types_allowed = True

    #17841460418095214
    #100599793108367P
    #EAASZB6VduVlMBAAQCjVahF13FTlTtcvtsiQlSyXQ0H48tSazdGZBZAZC2lENNbHXWMZANRIZC9l78sHMMbMEGXcaqjFdZBdFhMSnZAPw7syF50KwyB94BnUWErM9puJqKWhODBIAQGDcbgMmITL2qAUDzR4S28jDmq7OlLXE80qXDt6rZCfkhbtgXuaBYIcFPXEoapCw4rraC23HQ2ba3o84L
    def _execute(self, caption: str) -> str:
        """
        Execute the Instagram tool.

        Args:
            query : The query to search for.

        Returns:
            Search result summary along with related links
        """
        
        # Set your access token and photo URL
        print("***********************INSTA TOOL CALLED************************")
        user_access_token = self.get_tool_config("USER_ACCESS_TOKEN")
        insta_bussiness_account_id=self.get_tool_config("INSTAGRAM_BUSINESS_ACCOUNT_ID")

        if user_access_token is None:
            return "Error: Missing user access token."

        if insta_bussiness_account_id is None:
            return "Error: Missing insta bussiness account id."
        #####################

        #functionality to get URL of the image generated from prompt

        #####################
        image_url="https://wallpaperaccess.com/full/1198080.jpg"
        response = requests.post(
            f"https://graph.facebook.com/v17.0/{insta_bussiness_account_id}/media?image_url={image_url}&access_token={user_access_token}"
        )

        if response.status_code != 200:
            return f"Non-200 response: {str(response.text)}"
        
        data = response.json()
        container_ID=data["id"]
        response = requests.post(
            f"https://graph.facebook.com/v17.0/{insta_bussiness_account_id}/media_publish?creation_id={container_ID}&access_token={user_access_token}",
        )
        
        if response.status_code != 200:
            return f"Non-200 response: {str(response.text)}"

        print('************************Photo posted successfully!')
    
        return "Photo posted successfully!"

