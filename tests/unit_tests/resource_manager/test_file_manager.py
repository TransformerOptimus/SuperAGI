import pytest
from unittest.mock import Mock, patch, MagicMock
from superagi.models.resource import Resource
from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from superagi.lib.logger import logger

from superagi.resource_manager.file_manager import FileManager


@pytest.fixture
def resource_manager():
    session_mock = Mock()
    resource_manager = FileManager(session_mock)
    # resource_manager.agent_id = 1  # replace with actual value
    return resource_manager


@pytest.fixture
def mock_get_s3_client():
    with patch('superagi.helper.s3_helper.S3Helper.get_s3_client') as mock:
        yield mock


def test_write_binary_file(resource_manager):
    with patch.object(ResourceHelper, 'get_resource_path', return_value='test_path'), \
            patch.object(ResourceHelper, 'make_written_file_resource',
                         return_value=Resource(name='test.png', storage_type='S3')), \
            patch.object(S3Helper, 'upload_file'), \
            patch.object(logger, 'info') as logger_mock:
        result = resource_manager.write_binary_file('test.png', b'data')
        assert result == "Binary test.png saved successfully"
        logger_mock.assert_called_once_with("Binary test.png saved successfully")


def test_write_file(resource_manager):
    with patch.object(ResourceHelper, 'get_resource_path', return_value='test_path'), \
            patch.object(ResourceHelper, 'make_written_file_resource',
                         return_value=Resource(name='test.txt', storage_type='S3')), \
            patch.object(S3Helper, 'upload_file'), \
            patch.object(logger, 'info') as logger_mock:
        result = resource_manager.write_file('test.txt', 'content')
        assert result == "test.txt - File written successfully"
        logger_mock.assert_called_once_with("test.txt - File written successfully")


def test_read_from_s3_success(resource_manager, mock_get_s3_client):
    # Mock S3 client and response
    mock_s3_client = MagicMock()
    mock_response = {
        'ResponseMetadata': {'HTTPStatusCode': 200},
        'Body': MagicMock(read=MagicMock(return_value=b'Test content'))
    }
    mock_get_s3_client.return_value = mock_s3_client
    mock_s3_client.get_object.return_value = mock_response

    # Call the method under test
    file_path = "/example.txt"
    result = resource_manager.read_from_s3(file_path)

    # Assert the expected behavior
    assert result == 'Test content'
    mock_get_s3_client.assert_called_once()


def test_read_from_s3_error(resource_manager,mock_get_s3_client):
    # Mock S3 client and response
    mock_s3_client = MagicMock()
    mock_response = {
        'ResponseMetadata': {'HTTPStatusCode': 404}
    }
    mock_get_s3_client.return_value = mock_s3_client
    mock_s3_client.get_object.return_value = mock_response

    # Call the method under test and assert the exception
    file_path = "/example.txt"
    with pytest.raises(Exception):
        resource_manager.read_from_s3(file_path)

    mock_get_s3_client.assert_called_once()
