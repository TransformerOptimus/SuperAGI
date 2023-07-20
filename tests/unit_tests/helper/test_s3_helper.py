from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import BotoCoreError

from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper


@pytest.fixture
def mock_boto3_client():
    with patch('superagi.helper.s3_helper.boto3.client') as mock:
        yield mock


@pytest.fixture
def s3_helper():
    s3_helper = S3Helper()
    s3_helper.s3 = MagicMock()
    return s3_helper


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


def test_upload_file(s3_helper):
    # Mock file object and call the upload_file method
    file_mock = MagicMock()
    s3_helper.upload_file(file_mock, "test_path")

    # Assert that the upload_fileobj method was called with the correct arguments
    s3_helper.s3.upload_fileobj.assert_called_once_with(file_mock, s3_helper.bucket_name, "test_path")


def test_check_file_exists_in_s3(s3_helper):
    # Mock the response from S3
    response_mock = {
        'Contents': [{'Key': 'resources/test_file.txt'}]
    }
    s3_helper.s3.list_objects_v2.return_value = response_mock

    # Call the check_file_exists_in_s3 method
    result = s3_helper.check_file_exists_in_s3("/test_file.txt")

    # Assert that the method returns True when the file exists
    assert result is True


def test_check_file_does_not_exist_in_s3(s3_helper):
    # Mock the response from S3 where the file does not exist
    response_mock = {}
    s3_helper.s3.list_objects_v2.return_value = response_mock

    # Call the check_file_exists_in_s3 method
    result = s3_helper.check_file_exists_in_s3("/non_existing_file.txt")

    # Assert that the method returns False when the file does not exist
    assert result is False


def test_read_from_s3(s3_helper):
    # Mock the response from S3
    response_mock = {
        'ResponseMetadata': {'HTTPStatusCode': 200},
        'Body': MagicMock(read=MagicMock(return_value=b'File content')),  # Use bytes for the mock response
    }
    s3_helper.s3.get_object.return_value = response_mock

    # Call the read_from_s3 method
    result = s3_helper.read_from_s3("/test_file.txt")

    # Assert that the method returns the correct file content
    assert result == 'File content'


def test_read_from_s3_failure(s3_helper):
    # Mock the response from S3 where reading fails
    response_mock = {
        'ResponseMetadata': {'HTTPStatusCode': 500},
    }
    s3_helper.s3.get_object.return_value = response_mock

    # Call the read_from_s3 method and expect it to raise an Exception
    with pytest.raises(Exception):
        s3_helper.read_from_s3("/test_file.txt")
