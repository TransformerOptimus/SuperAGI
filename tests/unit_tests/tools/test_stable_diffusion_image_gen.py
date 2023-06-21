import base64
from io import BytesIO
from unittest.mock import patch, Mock

import pytest
from PIL import Image

from superagi.tools.image_generation.stable_diffusion_image_gen import StableDiffusionImageGenTool


def create_sample_image_base64():
    image = Image.new('RGBA', size=(50, 50), color=(73, 109, 137))
    byte_arr = BytesIO()
    image.save(byte_arr, format='PNG')
    encoded_image = base64.b64encode(byte_arr.getvalue())
    return encoded_image.decode('utf-8')


@pytest.fixture
def stable_diffusion_tool():
    with patch('superagi.tools.image_generation.stable_diffusion_image_gen.get_config') as get_config_mock, \
         patch('superagi.tools.image_generation.stable_diffusion_image_gen.requests.post') as post_mock, \
         patch('superagi.tools.image_generation.stable_diffusion_image_gen.ResourceManager') as resource_manager_mock:
        get_config_mock.return_value = 'fake_api_key'

        # Create a mock response object
        response_mock = Mock()
        response_mock.status_code = 200
        response_mock.json.return_value = {
            'artifacts': [{'base64': create_sample_image_base64()} for _ in range(2)]
        }
        post_mock.return_value = response_mock

        resource_manager_mock.write_binary_file.return_value = None

        yield

def test_execute(stable_diffusion_tool):
    tool = StableDiffusionImageGenTool()
    tool.resource_manager = Mock()
    result = tool._execute('prompt', ['img1.png', 'img2.png'])

    assert result == 'Images downloaded and saved successfully'
    tool.resource_manager.write_binary_file.assert_called()

def test_call_stable_diffusion(stable_diffusion_tool):
    tool = StableDiffusionImageGenTool()
    response = tool.call_stable_diffusion('fake_api_key', 512, 512, 2, 'prompt', 50)

    assert response.status_code == 200
    assert 'artifacts' in response.json()