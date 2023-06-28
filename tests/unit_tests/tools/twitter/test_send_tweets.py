import unittest
from unittest.mock import MagicMock, patch, Mock
from superagi.tools.twitter.send_tweets import SendTweetsTool
from superagi.helper.twitter_tokens import TwitterTokens
from superagi.helper.twitter_helper import TwitterHelper

class TestSendTweets(unittest.TestCase):

    def setUp(self):
        self.test_input = {
            "tweet_text": "Hello, world!",
            "is_media": False,
            "media_num": 0,
            "media_files": []
        }
        self.send_tweets_instance = SendTweetsTool()
        self.twitter_helper_instance = TwitterHelper()

    def test_execute_success(self):
       with patch.object(TwitterHelper, 'send_tweets', return_value=MagicMock(status_code=201)) as mock_send_tweets, \
            patch.object(TwitterTokens, 'get_twitter_creds', return_value={}) as mock_get_twitter_creds:
            send_tweets_tool = SendTweetsTool()
            send_tweets_tool.toolkit_config.toolkit_id = Mock()
            send_tweets_tool.toolkit_config.toolkit_id.return_value = 97
            response = send_tweets_tool._execute(False, tweet_text='Test tweet')
            self.assertEqual(response, "Tweet posted successfully!!")
            mock_send_tweets.assert_called()

    def test_execute_error(self):
        with patch.object(TwitterHelper, 'send_tweets', return_value=MagicMock(status_code=400)) as mock_send_tweets, \
            patch.object(TwitterTokens, 'get_twitter_creds', return_value={}) as mock_get_twitter_creds:
            send_tweets_tool = SendTweetsTool()
            send_tweets_tool.toolkit_config.toolkit_id = Mock()
            send_tweets_tool.toolkit_config.toolkit_id.return_value = 97
            response = send_tweets_tool._execute(False, tweet_text='Test tweet')
            self.assertEqual(response, "Error posting tweet. (Status code: 400)")
            mock_send_tweets.assert_called()

if __name__ == '__main__':
    unittest.main()
