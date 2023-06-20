import os
import base64
from PIL import Image
from io import BytesIO
import pytest
from unittest.mock import MagicMock, patch
from superagi.models.resource import Resource
import requests
from superagi.tools.image_generation.stable_diffusion_image_gen import StableDiffusionImageGenTool
from superagi.config.config import get_config
from superagi.helper.resource_helper import ResourceHelper


def mock_get_config(key):
    mock_configs = {
        "STABILITY_API_KEY": "api_key",
        "ENGINE_ID": "engine_id",
        "RESOURCES_OUTPUT_ROOT_DIR": get_config("RESOURCES_OUTPUT_ROOT_DIR"),
    }
    return mock_configs.get(key)


def mock_make_written_file_resource(self, *args, **kwargs):
    resource = Resource()
    resource.id = 1
    resource.path = "workspace/output"
    # resource_helper = ResourceHelper()
    resource.channel = 'OUTPUT'
    resource.storage_type = 'FILE'
    return resource


def mock_post(url, headers=None, json=None):
    response = MagicMock(status_code=200)
    buffer = BytesIO()
    img = Image.new("RGB", (512, 512), "white")
    img.save(buffer, "PNG")
    buffer.seek(0)
    img_data = buffer.getvalue()
    encoded_image_data = base64.b64encode(img_data).decode()
    response.json = lambda: {
        "artifacts": [
            {"base64": encoded_image_data},
            {"base64": encoded_image_data}
        ]
    }
    return response

@pytest.fixture(autouse=True)
def mock_written_file_resource(monkeypatch):
    monkeypatch.setattr(ResourceHelper, 'make_written_file_resource', mock_make_written_file_resource)


@pytest.fixture
def tool():
    return StableDiffusionImageGenTool()


@pytest.fixture
def temp_dir():
    return get_config("RESOURCES_OUTPUT_ROOT_DIR")


@pytest.fixture
def image_names():
    return ['image1.png', 'image2.png']

@pytest.fixture
def mock_connect_db():
    session = MagicMock(add=MagicMock(return_value=None),
                        commit=MagicMock(return_value=None),
                        flush=MagicMock(return_value=None))
    return session


class MockSession:
    def add(self, instance):
        pass

    def commit(self):
        pass

    def flush(self):
        pass

    def connect(self):
        pass

    def close(self):
        pass

class MockConnectDB:
    def connect(self):
        return MockSession()


class TestStableDiffusionImageGenTool:

    # def test_execute(self, tool, monkeypatch, temp_dir, image_names, mock_connect_db):
    #     monkeypatch.setattr('superagi.tools.image_generation.stable_diffusion_image_gen.get_config', mock_get_config)
    #     monkeypatch.setattr(requests, 'post', mock_post)

    #     prompt = 'Artificial Intelligence'
    #     height = 512
    #     width = 512
    #     num = 2
    #     steps = 50

    #     # Create a MagicMock object that returns the result of the mock_make_written_file_resource function
    #     def mock_method(*args, **kwargs):
    #         return mock_make_written_file_resource(None, *args, **kwargs)

    #     # Patch the make_written_file_resource method with the mock_method
    #     with patch.object(ResourceHelper, 'make_written_file_resource', mock_method):
    #         with patch('superagi.tools.image_generation.stable_diffusion_image_gen.connect_db', lambda: mock_connect_db):
    #             response = tool._execute(prompt, image_names, width, height, num, steps)

        # with patch('superagi.tools.image_generation.stable_diffusion_image_gen.connect_db', lambda: mock_connect_db):
        #     response = tool._execute(prompt, image_names, width, height, num, steps)


    def test_execute(self, tool, monkeypatch, temp_dir, image_names, mock_connect_db):
        monkeypatch.setattr('superagi.tools.image_generation.stable_diffusion_image_gen.get_config', mock_get_config)
        monkeypatch.setattr(requests, 'post', mock_post)

        prompt = 'Artificial Intelligence'
        height = 512
        width = 512
        num = 2
        steps = 50

           # Create a MagicMock object that returns the result of the mock_make_written_file_resource function
        def mock_method(*args, **kwargs):
            return mock_make_written_file_resource(None, *args, **kwargs)

        # Patch the make_written_file_resource method with the mock_method
        with patch.object(ResourceHelper, 'make_written_file_resource', mock_method):
        #     with patch('superagi.tools.image_generation.stable_diffusion_image_gen.Session', lambda: MockSession):
        #         response = tool._execute(prompt, image_names, width, height, num, steps)
            monkeypatch.setattr('superagi.tools.image_generation.stable_diffusion_image_gen.connect_db', MockConnectDB)
            response = tool._execute(prompt, image_names, width, height, num, steps)


        assert response == "Images downloaded and saved successfully"

        for image_name in image_names:
            path = os.path.join(temp_dir, image_name)
            assert os.path.exists(path)
            
            with open(path, "rb") as file:
                img_data = base64.b64decode(mock_post(None).json()['artifacts'][0]['base64'])
                file_content = file.read()

                assert file_content == img_data

            os.remove(path)


    def test_call_stable_diffusion(self, tool, monkeypatch):
        monkeypatch.setattr('superagi.tools.image_generation.stable_diffusion_image_gen.get_config', mock_get_config)
        monkeypatch.setattr(requests, 'post', mock_post)

        api_key = mock_get_config("STABILITY_API_KEY")
        width = 512
        height = 512
        num = 2
        prompt = "Artificial Intelligence"
        steps = 50

        response = tool.call_stable_diffusion(api_key, width, height, num, prompt, steps)
        assert response.status_code == 200
        assert 'artifacts' in response.json()

    def test_upload_to_s3(self, tool, temp_dir, image_names):

        final_img = Image.new("RGB", (512, 512), "white")
        final_path = os.path.join(temp_dir, image_names[0])
        image_format = "PNG"
        file_name = image_names[0]

        mock_session = MagicMock()

        # Create a MagicMock object that returns the result of the mock_make_written_file_resource function
        def mock_method(*args, **kwargs):
            return mock_make_written_file_resource(None, *args, **kwargs)

        # Patch the make_written_file_resource method with the mock_method
        with patch.object(ResourceHelper, 'make_written_file_resource', mock_method):
            tool.upload_to_s3(final_img, final_path, image_format, file_name, mock_session)

        assert os.path.exists(final_path)

        os.remove(final_path)


    def test_build_file_path(self, tool, monkeypatch, temp_dir, image_names):
        monkeypatch.setattr('superagi.tools.image_generation.stable_diffusion_image_gen.get_config', mock_get_config)

        image = image_names[0]
        root_dir = mock_get_config("RESOURCES_OUTPUT_ROOT_DIR")
        final_path = os.path.join(root_dir, image)

        result = tool.build_file_path(image, root_dir)
        assert os.path.abspath(result) == os.path.abspath(final_path)


if __name__ == "__main__":
    pytest.main()