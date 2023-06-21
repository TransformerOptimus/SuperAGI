import os
import unittest
from unittest.mock import patch, MagicMock

from superagi.tools.image_generation.dalle_image_gen import ImageGenTool


class TestImageGenTool(unittest.TestCase):

    @patch('openai.Image.create')
    @patch('requests.get')
    @patch('superagi.tools.image_generation.dalle_image_gen.get_config')
    def test_image_gen_tool_execute(self, mock_get_config, mock_requests_get, mock_openai_create):
        # Setup
        tool = ImageGenTool()
        prompt = 'Artificial Intelligence'
        image_names = ['image1.png', 'image2.png']
        size = 512
        num = 2

        # Mock responses
        mock_get_config.return_value = "/tmp"
        mock_openai_create.return_value = MagicMock(_previous=MagicMock(data=[
            {"url": "https://example.com/image1.png"},
            {"url": "https://example.com/image2.png"}
        ]))
        mock_requests_get.return_value.content = b"image_data"

        # Run the method under test
        response = tool._execute(prompt, image_names, size, num)

        # Assert the method ran correctly
        self.assertEqual(response, "Images downloaded successfully")
        for image_name in image_names:
            path = "/tmp/" + image_name
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as file:
                self.assertEqual(file.read(), b"image_data")

        # Clean up
        for image_name in image_names:
            os.remove("/tmp/" + image_name)


if __name__ == '__main__':
    unittest.main()