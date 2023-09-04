import pytest
from unittest.mock import Mock, patch
from superagi.models.resource import Resource
from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from superagi.lib.logger import logger

from superagi.resource_manager.file_manager import FileManager

@pytest.fixture
def resource_manager():
    session_mock = Mock()
    resource_manager = FileManager(session_mock)
    #resource_manager.agent_id = 1  # replace with actual value
    return resource_manager


def test_write_binary_file(resource_manager):
    with patch.object(ResourceHelper, 'get_resource_path', return_value='test_path'), \
            patch.object(ResourceHelper, 'make_written_file_resource',
                         return_value=Resource(name='test.png', storage_type='S3')), \
            patch.object(S3Helper, 'upload_file'), \
            patch.object(logger, 'info') as logger_mock:
        result = resource_manager.write_binary_file('test.png', b'data')
        assert result == "Binary test.png saved successfully"
        logger_mock.assert_called_once_with("Binary test.png saved successfully")


def test_write_txt_file(resource_manager):
    with patch.object(ResourceHelper, 'get_resource_path', return_value='test_path'), \
            patch.object(ResourceHelper, 'make_written_file_resource',
                         return_value=Resource(name='test.txt', storage_type='S3')), \
            patch.object(S3Helper, 'upload_file'), \
            patch.object(logger, 'info') as logger_mock:
        result = resource_manager.write_file('test.txt', 'content')
        assert result == "test.txt - File written successfully"
        logger_mock.assert_called_once_with("test.txt - File written successfully")

def test_write_pdf_file(resource_manager):
    with patch.object(ResourceHelper, 'get_resource_path', return_value='test_path'), \
            patch.object(ResourceHelper, 'make_written_file_resource',
                         return_value=Resource(name='test.pdf', storage_type='S3')), \
            patch.object(S3Helper, 'upload_file'), \
            patch.object(logger, 'info') as logger_mock:
        result = resource_manager.write_file('test.pdf', 'content')
        assert result == "test.pdf - File written successfully"
        logger_mock.assert_called_once_with("test.pdf - File written successfully")
        
def test_write_docx_file(resource_manager):
    with patch.object(ResourceHelper, 'get_resource_path', return_value='test_path'), \
            patch.object(ResourceHelper, 'make_written_file_resource',
                         return_value=Resource(name='test.docx', storage_type='S3')), \
            patch.object(S3Helper, 'upload_file'), \
            patch.object(logger, 'info') as logger_mock:
        result = resource_manager.write_file('test.docx', 'content')
        assert result == "test.docx - File written successfully"
        logger_mock.assert_called_once_with("test.docx - File written successfully")

def test_read_file(resource_manager):
    with patch.object(ResourceHelper, 'get_resource_path', return_value='test_path'), \
            patch.object(logger, 'info') as logger_mock, \
            patch('builtins.open', create=True) as mock_open:
        mock_file = mock_open.return_value
        mock_file.read.return_value = 'file content'
        result = resource_manager.read_file('test.txt')
        assert result == 'file content'
        logger_mock.assert_called_once_with("test.txt - File read successfully")