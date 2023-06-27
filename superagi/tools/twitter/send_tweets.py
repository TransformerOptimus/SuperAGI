import os
import json
import base64
import requests
from typing import Any, Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.helper.twitter_tokens import TwitterTokens
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth1Session
from superagi.helper.resource_helper import ResourceHelper

class SendTweetsInput(BaseModel):
    tweet_text: str = Field(..., description="Tweet text to be posted from twitter handle, if no value is given keep the default value as 'None'")
    is_media: bool = Field(..., description="'True' if there is any media to be posted with Tweet else 'False'.")
    media_num: int = Field(..., description="Integer value for the number of media files to be uploaded, default value is 0")
    media_files: list = Field(..., description="Name of the media files to be uploaded.")

class SendTweetsTool(BaseTool):
    name: str = "Send Tweets Tool"
    args_schema: Type[BaseModel] = SendTweetsInput
    description: str = "Send and Schedule Tweets for your Twitter Handle"
    agent_id: int = None

    def _execute(self, is_media: bool, tweet_text: str = 'None', media_num: int = 0, media_files: list = []):
        toolkit_id = self.toolkit_config.toolkit_id
        creds = TwitterTokens().get_twitter_creds(toolkit_id)
        params = {}
        if is_media:
            media_ids = self.get_media_ids(media_files, creds)
            params["media"] = {"media_ids": media_ids}
        if tweet_text is not None:
            params["text"] = tweet_text
        tweet_response = self.send_tweets(params, creds)
        if tweet_response.status_code ==  201:
            return "Tweet posted successfully!!"
        else:
            return "Error posting tweet. (Status code: {})".format(tweet_response.status_code)


    def get_media_ids(self, media_files, creds):
        media_ids = []
        oauth = OAuth1(creds["api_key"],
                    client_secret=creds["api_key_secret"],
                    resource_owner_key=creds["oauth_token"],
                    resource_owner_secret=creds["oauth_token_secret"])
        for file in media_files:
            file_path = self.get_file_path(file)
            image_data = open(file_path, 'rb').read()
            b64_image = base64.b64encode(image_data)
            upload_endpoint = 'https://upload.twitter.com/1.1/media/upload.json'
            headers = {'Authorization': 'application/octet-stream'}
            response = requests.post(upload_endpoint, headers=headers,
                             data={'media_data': b64_image},
                             auth=oauth)
            ids = json.loads(response.text)['media_id']
            media_ids.append(str(ids))

        return media_ids

    def get_file_path(self, file_name):
        output_root_dir = ResourceHelper.get_root_output_dir()

        final_path = ResourceHelper.get_root_input_dir() + file_name
        if "{agent_id}" in final_path:
            final_path = final_path.replace("{agent_id}", str(self.agent_id))

        if final_path is None or not os.path.exists(final_path):
            if output_root_dir is not None:
                final_path = ResourceHelper.get_root_output_dir() + file_name
                if "{agent_id}" in final_path:
                    final_path = final_path.replace("{agent_id}", str(self.agent_id))

        if final_path is None or not os.path.exists(final_path):
            raise FileNotFoundError(f"File '{file_name}' not found.")

        return final_path

    def send_tweets(self, params, creds):
        tweet_endpoint = "https://api.twitter.com/2/tweets"
        oauth = OAuth1Session(creds["api_key"],
                    client_secret=creds["api_key_secret"],
                    resource_owner_key=creds["oauth_token"],
                    resource_owner_secret=creds["oauth_token_secret"])

        response = oauth.post(tweet_endpoint,json=params)
        return response