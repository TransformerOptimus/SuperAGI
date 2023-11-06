import base64
from io import BytesIO
from unittest.mock import patch, Mock

import pytest
from PIL import Image

from superagi.tools.image_generation.stable_diffusion_image_gen import StableDiffusionImageGenTool

def mock_get_tool_config(key):
    configs = {
        'STABILITY_API_KEY': 'fake_api_key',
        'ENGINE_ID': 'engine_id_1',
    }
    return configs.get(key)


def create_sample_image_base64():
    image = Image.new('RGBA', size=(50, 50), color=(73, 109, 137))
    byte_arr = BytesIO()
    image.save(byte_arr, format='PNG')
    encoded_image = base64.b64encode(byte_arr.getvalue())
    return encoded_image.decode('utf-8')


@pytest.fixture
def stable_diffusion_tool():
    with patch('superagi.tools.image_generation.stable_diffusion_image_gen.requests.post') as post_mock, \
            patch(
                'superagi.tools.image_generation.stable_diffusion_image_gen.FileManager') as resource_manager_mock, \
                patch(
                'superagi.tools.image_generation.stable_diffusion_image_gen.ResourceHelper') as resource_helper_mock, \
                    patch(
                        'superagi.tools.image_generation.stable_diffusion_image_gen.Agent') as agent_mock, \
                        patch(
                        'superagi.tools.image_generation.stable_diffusion_image_gen.AgentExecution') as agent_execution_mock:

        # Create a mock response object
        response_mock = Mock()
        response_mock.status_code = 200
        response_mock.json.return_value = {
            'artifacts': [{'base64': create_sample_image_base64()} for _ in range(2)]
        }
        post_mock.return_value = response_mock

        resource_manager_mock.write_binary_file.return_value = None

        # Mock Agent and AgentExecution to return dummy values
        agent_mock.get_agent_from_id.return_value = Mock()
        agent_execution_mock.get_agent_execution_from_id.return_value = Mock()

        yield


def test_execute(stable_diffusion_tool):
    tool = StableDiffusionImageGenTool()
    tool.resource_manager = Mock()
    tool.agent_id = 123  # Use a dummy agent_id for testing purposes
    tool.toolkit_config.get_tool_config = lambda key: 'fake_api_key' if key == 'STABILITY_API_KEY' else 'engine_id_1'
    prompt = 'Test prompt'
    image_names = ['img1.png', 'img2.png']
    expected_result = 'Images downloaded and saved successfully'
    result = tool._execute(prompt, image_names)
    assert result.startswith(expected_result)
    tool.resource_manager.write_binary_file.assert_called()

def test_call_stable_diffusion(stable_diffusion_tool):
    tool = StableDiffusionImageGenTool()
    tool.toolkit_config.get_tool_config = mock_get_tool_config
    response = tool.call_stable_diffusion('fake_api_key', 512, 512, 2, 'prompt', 50)

    assert response.status_code == 200
    assert 'artifacts' in response.json()