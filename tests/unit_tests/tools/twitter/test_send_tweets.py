import unittest
import os
from unittest.mock import MagicMock, patch,
from superagi.tools.twitter.send_tweets import SendTweetsTool, SendTweetsInput
from superagi.helper.twitter_tokens import TwitterTokens

class TestSendTweets(unittest.TestCase):

    def setUp(self):
        self.test_input = {
            "tweet_text": "Hello, world!",
            "is_media": False,
            "media_num": 0,
            "media_files": []
        }
        self.send_tweets_instance = SendTweetsTool()

    def test_execute_success(self):
       with patch.object(SendTweetsTool, 'send_tweets', return_value=MagicMock(status_code=201)) as mock_send_tweets, \
            patch.object(TwitterTokens, 'get_twitter_creds', return_value={}) as mock_get_twitter_creds, \
            patch('send_tweets_tool.SendTweetsTool.toolkit_config', new_callable=PropertyMock, return_value=MagicMock(toolkit_id=1)):
            send_tweets_tool = SendTweetsTool()
            response = send_tweets_tool._execute(False, tweet_text='Test tweet')
            self.assertEqual(response, "Tweet posted successfully!!")
            mock_send_tweets.assert_called()

    def test_execute_error(self):
        with patch.object(SendTweetsTool, 'send_tweets', return_value=MagicMock(status_code=400)) as mock_send_tweets, \
            patch.object(TwitterTokens, 'get_twitter_creds', return_value={}) as mock_get_twitter_creds:
            send_tweets_tool = SendTweetsTool()
            response = send_tweets_tool._execute(False, tweet_text='Test tweet')
            self.assertEqual(response, "Error posting tweet. (Status code: 400)")
            mock_send_tweets.assert_called()
    
    def test_get_media_ids(self):
        test_creds = {
            "api_key": "test_key",
            "api_key_secret": "test_key_secret",
            "oauth_token": "test_token",
            "oauth_token_secret": "test_token_secret"
        }
        
        with patch('requests.post') as mock_request:
            mock_request.return_value.text = '{"media_id": "1234567890"}'
            media_ids = self.send_tweets_instance.get_media_ids(["downloads.png"], test_creds)
            self.assertEqual(media_ids, ["1234567890"])

        with patch('requests.post') as mock_request:
            mock_request.return_value.text = '{"media_id": "0987654321"}'
            media_ids = self.send_tweets_instance.get_media_ids(["testing.png"], test_creds)
            self.assertEqual(media_ids, ["0987654321"])

    def test_send_tweets(self):
        test_params = {
            "text": "Hello, world!"
        }
        test_creds = {
            "api_key": "test_key",
            "api_key_secret": "test_key_secret",
            "oauth_token": "test_token",
            "oauth_token_secret": "test_token_secret"
        }

        with patch('requests_oauthlib.OAuth1Session.post') as mock_oauth_request:
            mock_oauth_request.return_value.status_code = 201
            response = self.send_tweets_instance.send_tweets(test_params, test_creds)
            self.assertEqual(response.status_code, 201)

        with patch('requests_oauthlib.OAuth1Session.post') as mock_oauth_request:
            mock_oauth_request.return_value.status_code = 400
            response = self.send_tweets_instance.send_tweets(test_params, test_creds)
            self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()