import unittest
from unittest.mock import patch, Mock, MagicMock
from typing import NamedTuple
import ast
from sqlalchemy.orm import Session
from superagi.helper.twitter_tokens import Creds, TwitterTokens
from superagi.models.toolkit import Toolkit
from superagi.models.oauth_tokens import OauthTokens
import time
import http.client


class TestCreds(unittest.TestCase):
    def test_init(self):
        creds = Creds('api_key', 'api_key_secret', 'oauth_token', 'oauth_token_secret')
        self.assertEqual(creds.api_key, 'api_key')
        self.assertEqual(creds.api_key_secret, 'api_key_secret')
        self.assertEqual(creds.oauth_token, 'oauth_token')
        self.assertEqual(creds.oauth_token_secret, 'oauth_token_secret')


class TestTwitterTokens(unittest.TestCase):
    twitter_tokens = TwitterTokens(Session)
    def setUp(self):
        self.mock_session = Mock(spec=Session)
        self.twitter_tokens = TwitterTokens(session=self.mock_session)

    def test_init(self):
        self.assertEqual(self.twitter_tokens.session, self.mock_session)

    def test_percent_encode(self):
        self.assertEqual(self.twitter_tokens.percent_encode("#"), "%23")
        
    def test_gen_nonce(self):
        self.assertEqual(len(self.twitter_tokens.gen_nonce()), 32)
    
    @patch.object(time, 'time', return_value=1234567890)
    @patch.object(http.client, 'HTTPSConnection')
    @patch('superagi.helper.twitter_tokens.TwitterTokens.gen_nonce', return_value=123456)  # Replace '__main__' with actual module name
    @patch('superagi.helper.twitter_tokens.TwitterTokens.percent_encode', return_value="encoded")  # Replace '__main__' with actual module name
    def test_get_request_token(self, mock_percent_encode, mock_gen_nonce, mock_https_connection, mock_time):
        response_mock = Mock()
        response_mock.read.return_value = b'oauth_token=test_token&oauth_token_secret=test_secret'
        mock_https_connection.return_value.getresponse.return_value = response_mock

        api_data = {"api_key": "test_key", "api_secret": "test_secret"}
        expected_result = {'oauth_token': 'test_token', 'oauth_token_secret': 'test_secret'}
        self.assertEqual(self.twitter_tokens.get_request_token(api_data), expected_result)

if __name__ == "__main__":
    unittest.main()