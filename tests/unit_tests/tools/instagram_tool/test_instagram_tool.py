import pytest
from superagi.tools.instagram_tool.instagram import InstagramTool
from unittest.mock import MagicMock, patch

# Create a fixture for the InstagramTool instance
@pytest.fixture
def instagram_tool():
    return InstagramTool()

def test_execute_missing_meta_user_access_token(instagram_tool):
    # Test for the case when META_USER_ACCESS_TOKEN is missing

    # Mock the get_tool_config method to return None for META_USER_ACCESS_TOKEN
    instagram_tool.toolkit_config.get_tool_config = MagicMock(return_value=None)

    # Call the _execute method
    result = instagram_tool._execute("A beautiful sunset")

    # Verify the output
    assert result == "Error: Missing meta user access token."

def test_execute_missing_facebook_page_id(instagram_tool):
    # Test for the case when FACEBOOK_PAGE_ID is missing

    # Mock the get_tool_config method to return None for FACEBOOK_PAGE_ID
    instagram_tool.toolkit_config.get_tool_config = MagicMock(side_effect=lambda key: "your_meta_user_access_token" if key == "META_USER_ACCESS_TOKEN" else None)

    # Call the _execute method
    result = instagram_tool._execute("A beautiful sunset")

    # Verify the output
    assert result == "Error: Missing facebook page id."

def test_get_file_path_from_image_generation_tool(instagram_tool):
    # Test for the get_file_path_from_image_generation_tool method
    # Mock the tool_response_manager to return a response
    instagram_tool.tool_response_manager = MagicMock()
    instagram_tool.tool_response_manager.get_last_response.return_value = "['/path/to/image.jpg']"
    file_path = instagram_tool.get_file_path_from_image_generation_tool()
    assert file_path == "resources/path/to/image.jpg"


def test_get_img_public_url(instagram_tool):
    # Test for the get_img_public_url method
    # Mock the S3 client and its put_object method
    s3_client_mock = MagicMock()
    s3_client_mock.get_object.return_value = {"Body": MagicMock(read=lambda: b"image_content")}
    with patch.object(InstagramTool, 'create_s3_client', return_value=s3_client_mock):
        file_path = "path/to/image.jpg"
        content = b"image_content"
        image_url = instagram_tool.get_img_public_url(s3_client_mock, file_path, content)
        assert image_url.startswith("https://")
        assert file_path.split("/")[-1] in image_url

def test_get_req_insta_id(instagram_tool):
    # Test for the get_req_insta_id method
    # Mock the requests.get method
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"instagram_business_account": {"id": "account_id"}}
    with patch("requests.get", return_value=response_mock):
        root_api_url = "https://graph.facebook.com/v17.0/"
        facebook_page_id = "page_id"
        meta_user_access_token = "access_token"
        response = instagram_tool.get_req_insta_id(root_api_url, facebook_page_id, meta_user_access_token)
        assert response.status_code == 200
        assert response.json()["instagram_business_account"]["id"] == "account_id"

def test_post_media_container_id(instagram_tool):
    # Test for the post_media_container_id method
    # Mock the requests.post method
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"id": "container_id"}
    with patch("requests.post", return_value=response_mock):
        root_api_url = "https://graph.facebook.com/v17.0/"
        insta_business_account_id = "account_id"
        image_url = "https://example.com/image.jpg"
        encoded_caption = "encoded_caption"
        meta_user_access_token = "access_token"
        response = instagram_tool.post_media_container_id(root_api_url, insta_business_account_id, image_url, encoded_caption, meta_user_access_token)
        assert response.status_code == 200
        assert response.json()["id"] == "container_id"

def test_post_media(instagram_tool):
    # Test for the post_media method
    # Mock the requests.post method
    response_mock = MagicMock()
    response_mock.status_code = 200
    with patch("requests.post", return_value=response_mock):
        root_api_url = "https://graph.facebook.com/v17.0/"
        insta_business_account_id = "account_id"
        container_ID = "container_id"
        meta_user_access_token = "access_token"
        response = instagram_tool.post_media(root_api_url, insta_business_account_id, container_ID, meta_user_access_token)
        assert response.status_code == 200

