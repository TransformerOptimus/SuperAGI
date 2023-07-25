import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import NoCredentialsError
from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper


class TestS3Helper:
    @patch('superagi.helper.s3_helper.boto3.client')
    @patch('superagi.helper.s3_helper.get_config')
    def test_init(self, config_mock, boto3_mock):
        config_mock.return_value = "fake_bucket_name"
        helper = S3Helper()
        assert helper.bucket_name == "fake_bucket_name"
        assert boto3_mock.called
    
    @patch('superagi.helper.s3_helper.boto3.client')
    def test_get_s3_client(self, boto3_mock):
        S3Helper._S3Helper__get_s3_client()
        assert boto3_mock.called

    @patch.object(S3Helper, "_S3Helper__get_s3_client", return_value=MagicMock())
    def test_upload_file(self, s3_client_mock):
        s3_helper = S3Helper()
        try:
            s3_helper.upload_file(None, "")
        except Exception as err:
            assert isinstance(err, NoCredentialsError)

    @patch.object(S3Helper, "_S3Helper__get_s3_client", return_value=MagicMock())
    def test_get_json_file(self, s3_client_mock):
        s3_helper = S3Helper()
        try:
            s3_helper.get_json_file("")
        except Exception as err:
            assert isinstance(err, NoCredentialsError)
    
    @patch.object(S3Helper, "_S3Helper__get_s3_client", return_value=MagicMock())
    def test_check_file_exists_in_s3(self, s3_client_mock):
        s3_helper = S3Helper()
        assert not s3_helper.check_file_exists_in_s3("")

    @patch.object(S3Helper, "_S3Helper__get_s3_client", return_value=MagicMock())
    def test_read_from_s3(self, s3_client_mock):
        s3_helper = S3Helper()
        try:
            s3_helper.read_from_s3("")
        except Exception as err:
            assert isinstance(err, Exception)