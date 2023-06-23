from unittest.mock import Mock, patch
import pytest
from superagi.tools.image_generation.dalle_image_gen import DalleImageGenTool


class MockBaseLlm:
    def generate_image(self, prompt, size, num):
        return Mock(_previous={"data": [{"url": f"https://example.com/image_{i}.png"} for i in range(num)]})


class TestDalleImageGenTool:

    @pytest.fixture
    def tool(self):
        tool = DalleImageGenTool()
        tool.llm = MockBaseLlm()
        response_mock = Mock()
        tool.resource_manager = response_mock
        return tool

    @patch("requests.get")
    def test_execute(self, mock_get, tool):
        mock_get.return_value = Mock(content=b"fake image data")
        response = tool._execute("test prompt", ["test1.png", "test2.png"], size=512, num=2)
        assert response == "Images downloaded successfully"
        mock_get.assert_called_with("https://example.com/image_1.png")
        assert tool.resource_manager.write_binary_file.call_count == 2
