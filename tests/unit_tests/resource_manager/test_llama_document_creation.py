import pytest
from unittest.mock import patch, MagicMock
from superagi.resource_manager.resource_manager import ResourceManager


def test_create_llama_document_s3(mocker):
    agent_id = 'test_agent'
    resource_manager = ResourceManager(agent_id)

    mock_boto_client = MagicMock()
    mock_s3_obj = {
        'Body': MagicMock(read=MagicMock(return_value='mock_file_content'))
    }
    mock_boto_client.get_object.return_value = mock_s3_obj
    mocker.patch('boto3.client', return_value=mock_boto_client)

    mocker.patch('superagi.resource_manager.resource_manager.get_config',
                 side_effect=['mock_access_key', 'mock_secret_key', 'mock_bucket'])

    mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('os.remove')

    MockSimpleDirectoryReader = MagicMock()
    mocker.patch('superagi.resource_manager.resource_manager.SimpleDirectoryReader',
                 return_value=MockSimpleDirectoryReader)

    resource_manager.create_llama_document_s3('mock_file_path')

    mock_boto_client.get_object.assert_called_once_with(
        Bucket='mock_bucket',
        Key='mock_file_path')
    MockSimpleDirectoryReader.load_data.assert_called_once()


def test_create_llama_document_s3_file_path_provided(mocker):
    resource_manager = ResourceManager('test_agent')

    mock_boto_client = MagicMock()
    mocker.patch('boto3.client', return_value=mock_boto_client)

    mocker.patch('superagi.resource_manager.resource_manager.get_config',
                 side_effect=['mock_access_key', 'mock_secret_key', 'mock_bucket'])

    mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('os.remove')

    MockSimpleDirectoryReader = MagicMock()
    mocker.patch('superagi.resource_manager.resource_manager.SimpleDirectoryReader',
                 return_value=MockSimpleDirectoryReader)

    with pytest.raises(Exception, match="file_path must be provided"):
        resource_manager.create_llama_document_s3(None)