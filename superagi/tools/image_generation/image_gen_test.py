import unittest
from unittest import TestCase
from unittest.mock import patch
from superagi.tools.image_generation.dalle_image_gen import ImageGenTool
from superagi.config.config import get_config


class ImageGenToolTestCase(TestCase):

    def setUp(self):
        MOCK_OPEN_API_KEY = 'api key'
        MOCK_RESOURCES_OUTPUT_ROOT_DIR = 'resource directory path'
        self.tool = ImageGenTool()

    def test_execute(self):
        prompt = "Generate an image of 3 husky dogs"
        image_name = ["husky_dog_1.jpg", "husky_dog_2.jpg", "husky_dog_3.jpg"]
        size = 512
        num = 2
        result = self.tool._execute(prompt, image_name, size, num)
        assert result == "Images downloaded successfully"


if __name__ == '__main__':
    unittest.main()
