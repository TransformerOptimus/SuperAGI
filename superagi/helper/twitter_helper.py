import os
import json
import base64
import requests
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth1Session
from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.types.storage_types import StorageType
from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper


class TwitterHelper:

    def get_media_ids(self, session, media_files, creds, agent_id, agent_execution_id):
        media_ids = []
        oauth = OAuth1(creds.api_key,
                       client_secret=creds.api_key_secret,
                       resource_owner_key=creds.oauth_token,
                       resource_owner_secret=creds.oauth_token_secret)
        for file in media_files:
            file_path = self.get_file_path(session, file, agent_id, agent_execution_id)
            image_data = self._get_image_data(file_path)
            b64_image = base64.b64encode(image_data)
            upload_endpoint = 'https://upload.twitter.com/1.1/media/upload.json'
            headers = {'Authorization': 'application/octet-stream'}
            response = requests.post(upload_endpoint, headers=headers,
                                     data={'media_data': b64_image},
                                     auth=oauth)
            ids = json.loads(response.text)['media_id']
            media_ids.append(str(ids))
        return media_ids

    def get_file_path(self, session, file_name, agent_id, agent_execution_id):
        final_path = ResourceHelper().get_agent_read_resource_path(file_name,
                                                                    agent=Agent.get_agent_from_id(session, agent_id),
                                                                    agent_execution=AgentExecution.get_agent_execution_from_id(
                                                                  session, agent_execution_id))
        return final_path

    def _get_image_data(self, file_path):
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
                attachment_data = S3Helper().read_binary_from_s3(file_path)
        else:
            with open(file_path, "rb") as file:
                attachment_data = file.read()
        return attachment_data

    def send_tweets(self, params, creds):
        tweet_endpoint = "https://api.twitter.com/2/tweets"
        oauth = OAuth1Session(creds.api_key,
                              client_secret=creds.api_key_secret,
                              resource_owner_key=creds.oauth_token,
                              resource_owner_secret=creds.oauth_token_secret)

        response = oauth.post(tweet_endpoint, json=params)
        return response

    def _get_image_data(self, file_path):
        if get_config("STORAGE_TYPE") == StorageType.S3:
            return S3Helper().read_binary_from_s3(file_path)
        else:
            with open(file_path, "rb") as image_file:
                return image_file.read()
            