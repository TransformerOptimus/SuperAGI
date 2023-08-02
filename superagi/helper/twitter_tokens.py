import hmac
import time
import random
import base64
import hashlib
import urllib.parse
import ast
import http.client as http_client
from sqlalchemy.orm import Session
from superagi.models.toolkit import Toolkit
from superagi.models.oauth_tokens import OauthTokens
from superagi.config.config import get_config

class Creds:

    def __init__(self,api_key, api_key_secret, oauth_token, oauth_token_secret):
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

class TwitterTokens:

    def __init__(self, session: Session):
        self.session = session

    def get_request_token(self,api_data):
        api_key = api_data["api_key"]
        api_secret_key = api_data["api_secret"]
        http_method = 'POST'
        base_url = 'https://api.twitter.com/oauth/request_token'

        env = get_config("ENV", "DEV")
        if env == "DEV":
            oauth_callback = "http://localhost:3000/api/twitter/oauth-tokens"
        else:
            oauth_callback = "https://app.superagi.com/api/twitter/oauth-tokens"
        params = {
            'oauth_callback': oauth_callback,
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
        toolkit = self.session.query(Toolkit).filter(Toolkit.id == toolkit_id).first()
        organisation_id = toolkit.organisation_id
        twitter_creds = self.session.query(OauthTokens).filter(OauthTokens.toolkit_id == toolkit_id, OauthTokens.organisation_id == organisation_id).first()
        twitter_creds = ast.literal_eval(twitter_creds.value)
        final_creds = Creds(twitter_creds['api_key'], twitter_creds['api_key_secret'], twitter_creds['oauth_token'], twitter_creds['oauth_token_secret'])
        return final_creds