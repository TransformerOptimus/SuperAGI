import unittest
from unittest.mock import MagicMock, patch
from superagi.tools.twitter.send_tweets import SendTweetsTool

class TestSendTweetsTool(unittest.TestCase):

    @patch('your_module.requests.post')
    @patch('your_module.ResourceHelper.get_root_output_dir')
    @patch('your_module.ResourceHelper.get_root_input_dir')
    def test_get_media_ids(self, mock_get_input_dir, mock_get_output_dir, mock_requests_post):

        tool = SendTweetsTool()

        mock_get_input_dir.return_value = '/input/path/'
        mock_get_output_dir.return_value = '/output/path/'

        media_ids = [123, 456]
        responses = [
            MagicMock(text='{ "media_id": 123 }'),
            MagicMock(text='{ "media_id": 456 }')
        ]
        mock_requests_post.side_effect = responses

        media_files = ['image1.png', 'image2.png']
        creds = {...}

        result = tool.get_media_ids(media_files, creds)

        self.assertEqual(result, [str(id) for id in media_ids])

    @patch('your_module.OAuth1Session.post')
    def test_send_tweets(self, mock_oauth1_post):

        tool = SendTweetsTool()

        mock_oauth1_post.return_value = MagicMock(status_code=201)

        params = {
            "text": "Hello, World!"
        }
        creds = {...}

        response = tool.send_tweets(params, creds)

        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()