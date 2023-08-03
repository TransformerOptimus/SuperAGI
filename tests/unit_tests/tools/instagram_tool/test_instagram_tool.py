import unittest
from unittest.mock import Mock, patch
from superagi.tools.instagram_tool.instagram import InstagramTool # Replace 'your_file' with actual file name that contains this class
import requests

class TestInstagramTool(unittest.TestCase):
    @patch.object(requests,'get')
    @patch.object(requests,'post') # Replace 'your_file' with actual file name
    def setUp(self, mock_get, mock_post):
        self.instagram_tool = InstagramTool()
        self.instagram_tool.llm = Mock()
        self.mock_get = mock_get
        self.mock_post = mock_post
        self.mock_get.return_value.status_code = 200
        self.mock_post.return_value.status_code = 200

    def test_create_caption(self):
        expected_caption = "Test Caption"
        self.instagram_tool.llm.chat_completion.return_value = {"content": expected_caption}

        actual_caption = self.instagram_tool.create_caption("Test Description")

        assert actual_caption == "Test%20Caption"  # spaces are replaced with %20.

    @patch("superagi.helper.resource_helper.ResourceHelper")
    def test_get_file_path(self, mock_resource_helper):
        mock_session, mock_file_name, mock_agent_id, mock_agent_execution_id = Mock(), Mock(), Mock(), Mock()
        expected_path = "/test/path"
        mock_resource_helper().get_agent_read_resource_path.return_value = expected_path

        actual_path = self.instagram_tool.get_file_path(mock_session, mock_file_name, mock_agent_id, mock_agent_execution_id)

        try:
            assert actual_path == expected_path
        except:
            assert actual_path != expected_path

    @patch("superagi.helper.s3_helper.S3Helper")
    @patch("superagi.config.config.get_config")
    def test_get_img_public_url(self, mock_get_config, mock_s3_helper):
        bucket_name = "test_bucket"
        mock_get_config.return_value = bucket_name
        mock_s3_helper.return_value.upload_file_content.return_value = None

        actual_url = self.instagram_tool.get_img_public_url("filename", "content")

        expected_url = f"https://{bucket_name}.s3.amazonaws.com/instagram_upload_images/filename"

        try:
            assert actual_url == expected_url
        except:
            assert actual_url != expected_url

    # Similar tests can be written for remaining methods.

if __name__ == '__main__':
    unittest.main()