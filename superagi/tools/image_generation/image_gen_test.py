import unittest
from unittest.mock import patch
from .dalle_image_gen import ImageGenTool

class TestImageGenTool(unittest.TestCase):

    def setUp(self):
        self.tool = ImageGenTool()

    @patch('openai.Image.create')
    @patch('requests.get')
    @patch('builtins.open')

    def test_execute(self, mock_open, mock_requests_get, mock_openai_image_create):
        prompt = "Generate an image of 2 leather bags with a floral print on it."
        image_name = ['leather_bag_1.jpg','leather_bag_2,jpg']
        size = 512
        num = 2

        # Mocking the response from openai.Image.create
        response_data = [
            {'url': 'https://example.com/image1.jpg'},
            {'url': 'https://example.com/image2.jpg'}
        ]
        
        mock_openai_image_create.return_value._previous.data = response_data

        # Mocking the response from requests.get
        mock_requests_get.return_value.content = b'image_data'

        # Calling the execute method
        result = self.tool._execute(prompt, image_name, size, num)

        # Asserting the output
        self.assertEqual(result, "Images downloaded successfully")

        # Asserting the calls made to open, requests.get, and openai.Image.create
        expected_open_calls = [
            unittest.mock.call('image1.jpg', mode='wb'),
            unittest.mock.call().__enter__().write(b'image_data'),
            unittest.mock.call().__exit__(None, None, None),
            unittest.mock.call('image2.jpg', mode='wb'),
            unittest.mock.call().__enter__().write(b'image_data'),
            unittest.mock.call().__exit__(None, None, None)
        ]
        mock_open.assert_has_calls(expected_open_calls)
        mock_requests_get.assert_called_with('https://example.com/image1.jpg')
        mock_openai_image_create.assert_called_with(prompt=prompt, n=num, size='512x512')

if __name__ == '__main__':
    unittest.main()
