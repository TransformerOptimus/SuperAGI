import os
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
from io import BytesIO
import base64
from superagi.config.config import get_config

from superagi.tools.image_generation.stable_diffusion_image_gen import StableDiffusionImageGenTool


class TestStableDiffusionImageGenTool(unittest.TestCase):

    @patch('requests.post')
    @patch('superagi.tools.image_generation.stable_diffusion_image_gen.get_config')
    def test_stable_diffusion_image_gen_tool_execute(self, mock_get_config, mock_requests_post):
        # Setup
        tool = StableDiffusionImageGenTool()
        prompt = 'Artificial Intelligence'
        image_names = ['image1.png', 'image2.png']
        height = 512
        width = 512
        num = 2
        steps = 50

        # Create a temporary directory for image storage
        temp_dir = get_config("RESOURCES_OUTPUT_ROOT_DIR")

        # Mock responses
        mock_configs = {"STABILITY_API_KEY": "api_key", "ENGINE_ID": "engine_id", "RESOURCES_OUTPUT_ROOT_DIR": temp_dir}
        mock_get_config.side_effect = lambda k: mock_configs[k]

        # Prepare sample image bytes
        img = Image.new("RGB", (width, height), "white")
        buffer = BytesIO()
        img.save(buffer, "PNG")
        buffer.seek(0)
        img_data = buffer.getvalue()
        encoded_image_data = base64.b64encode(img_data).decode()

        # Use the proper base64-encoded string
        mock_requests_post.return_value = MagicMock(status_code=200, json=lambda: {
            "artifacts": [
                {"base64": encoded_image_data},
                {"base64": encoded_image_data}
            ]
        })

        # Run the method under test
        response = tool._execute(prompt, image_names, width, height, num, steps)
        self.assertEqual(response, f"Images downloaded successfully")

        for image_name in image_names:
            path = os.path.join(temp_dir, image_name)
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as file:
                self.assertEqual(file.read(), img_data)

        # Clean up
        for image_name in image_names:
            os.remove(os.path.join(temp_dir, image_name))

if __name__ == '__main__':
    unittest.main()
