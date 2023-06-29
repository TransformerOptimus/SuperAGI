import os
import pickle
import json
import hmac
import time
import random
import base64
import hashlib
import urllib.parse
import http.client as http_client
from superagi.config.config import get_config
from sqlalchemy.orm import Session
from superagi.models.tool_config import ToolConfig
from superagi.resource_manager.manager import ResourceManager

class Creds:

    def __init__(self,api_key, api_key_secret, oauth_token, oauth_token_secret):
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

class TwitterTokens:
    session: Session

    def get_request_token(self,api_data):
        api_key = api_data["api_key"]
        api_secret_key = api_data["api_secret"]
        http_method = 'POST'
        base_url = 'https://api.twitter.com/oauth/request_token'

        params = {
            'oauth_callback': 'http://localhost:3000/api/oauth-twitter',
            'oauth_consumer_key': api_key,
            'oauth_nonce': self.gen_nonce(),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': int(time.time()),
            'oauth_version': '1.0'
        }

        params_sorted = sorted(params.items())
        params_qs = '&'.join([f'{k}={self.percent_encode(str(v))}' for k, v in params_sorted])

        base_string = f'{http_method}&{self.percent_encode(base_url)}&{self.percent_encode(params_qs)}'

        signing_key = f'{self.percent_encode(api_secret_key)}&'
        signature = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
        params['oauth_signature'] = base64.b64encode(signature.digest()).decode()

        auth_header = 'OAuth ' + ', '.join([f'{k}="{self.percent_encode(str(v))}"' for k, v in params.items()])

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': auth_header
        }
        conn = http_client.HTTPSConnection("api.twitter.com")
        conn.request("POST", "/oauth/request_token", "", headers)
        res = conn.getresponse()
        response_data = res.read().decode('utf-8')
        conn.close()
        request_token_resp = dict(urllib.parse.parse_qsl(response_data))
        return request_token_resp

    def percent_encode(self, val):
        return urllib.parse.quote(val, safe='')

    def gen_nonce(self):
        nonce = ''.join([str(random.randint(0, 9)) for i in range(32)])
        return nonce

    def get_twitter_creds(self, toolkit_id):
        file_name = "twitter_credentials.pickle"
        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
        file_path = file_name
        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            file_path = root_dir + file_name
        else:
            file_path = os.getcwd() + "/" + file_name
        if os.path.exists(file_path):
            with open(file_path,'rb') as file:
                creds = pickle.load(file)
            if isinstance(creds, str):
                creds = json.loads(creds)
        twitter_creds = self.session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit_id).all()
        api_key = ""
        api_key_secret = ""
        for credentials in twitter_creds:
            credentials = credentials.__dict__
            if credentials["key"] == "TWITTER_API_KEY":
                api_key = credentials["value"]
            if credentials["key"] == "TWITTER_API_SECRET":
                api_key_secret = credentials["value"]
        final_creds = Creds(api_key, api_key_secret, creds["oauth_token"], creds["oauth_token_secret"])
        return final_creds