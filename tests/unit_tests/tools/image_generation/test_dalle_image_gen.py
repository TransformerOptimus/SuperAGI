from unittest.mock import patch, MagicMock

from superagi.tools.image_generation.dalle_image_gen import DalleImageGenTool


@patch('superagi.tools.image_generation.dalle_image_gen.OpenAiDalle')
@patch('superagi.tools.image_generation.dalle_image_gen.requests')
def test_execute_dalle_image_gen_tool(mock_requests, mock_dalle):
    # Arrange
    tool = DalleImageGenTool()
    tool.toolkit_config.get_tool_config = MagicMock(return_value="test_api_key")
    tool.resource_manager = MagicMock()
    mock_dalle_instance = mock_dalle.return_value
    mock_dalle_instance.generate_image.return_value = MagicMock(
        _previous=MagicMock(data=[
            {'url': 'http://test_url1.com'},
            {'url': 'http://test_url2.com'}
        ])
    )
    mock_requests.get.return_value.content = b"test_image_data"
    prompt = "test_prompt"
    size = 512
    num = 2
    image_names = ["image1.png", "image2.png"]

    # Act
    result = tool._execute(prompt, image_names, size, num)

    # Assert
    assert result == "Images downloaded successfully"
    mock_dalle.assert_called_once_with(api_key="test_api_key", number_of_results=num)
    mock_dalle_instance.generate_image.assert_called_once_with(prompt, size, num)
    tool.resource_manager.write_binary_file.assert_any_call("image1.png", b"test_image_data")
    tool.resource_manager.write_binary_file.assert_any_call("image2.png", b"test_image_data")