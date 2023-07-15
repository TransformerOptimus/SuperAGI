import pytest
from unittest.mock import MagicMock, patch
from superagi.helper.s3_helper import S3Helper
from superagi.config.config import get_config
from botocore.exceptions import BotoCoreError


@pytest.fixture
def mock_boto3_client():
    with patch('superagi.helper.s3_helper.boto3.client') as mock:
        yield mock


def test_upload_file_success(mock_boto3_client):
    # Mock S3 client and file
    mock_s3_client = MagicMock()
    mock_boto3_client.return_value = mock_s3_client
    mock_file = MagicMock()

    # Create an instance of the S3Helper class
    s3_helper = S3Helper()

    # Call the method under test
    path = "example/file.txt"
    s3_helper.upload_file(mock_file, path)

    # Assert the expected behavior
    mock_boto3_client.assert_called_with(
        's3',
        aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY")
    )
    mock_s3_client.upload_fileobj.assert_called_with(mock_file, get_config("BUCKET_NAME"), path)


def test_upload_file_exception(mock_boto3_client):
    # Mock S3 client and file
    mock_s3_client = MagicMock()
    mock_boto3_client.return_value = mock_s3_client
    mock_file = MagicMock()

    # Set up the exception scenario
    mock_s3_client.upload_fileobj.side_effect = BotoCoreError

    # Create an instance of the S3Helper class
    s3_helper = S3Helper()

    # Call the method under test and assert the exception
    path = "example/file.txt"
    with pytest.raises(Exception):
        s3_helper.upload_file(mock_file, path)

    mock_boto3_client.assert_called_with(
        's3',
        aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY")
    )
    mock_s3_client.upload_fileobj.assert_called_with(mock_file, get_config("BUCKET_NAME"), path)
