import pytest
from unittest.mock import patch
from superagi.helper.resource_helper import ResourceHelper

def test_make_written_file_resource(mocker):
    mocker.patch('os.getcwd', return_value='/')
    # mocker.patch('os.getcwd', return_value='/')
    mocker.patch('os.makedirs', return_value=None)
    mocker.patch('os.path.getsize', return_value=1000)
    mocker.patch('os.path.splitext', return_value=("", ".txt"))
    mocker.patch('superagi.helper.resource_helper.get_config', side_effect=['/', 'local', None])

    with patch('superagi.helper.resource_helper.logger') as logger_mock:
        result = ResourceHelper.make_written_file_resource('test.txt', 1, 'INPUT')

    assert result.name == 'test.txt'
    assert result.path == '/test.txt'
    assert result.storage_type == 'local'
    assert result.size == 1000
    assert result.type == 'application/txt'
    assert result.channel == 'OUTPUT'
    assert result.agent_id == 1

def test_get_resource_path(mocker):
    mocker.patch('os.getcwd', return_value='/')
    mocker.patch('superagi.helper.resource_helper.get_config', side_effect=['/'])

    result = ResourceHelper.get_resource_path('test.txt')

    assert result == '/test.txt'

def test_get_agent_resource_path(mocker):
    mocker.patch('os.getcwd', return_value='/')
    mocker.patch('os.makedirs')
    mocker.patch('superagi.helper.resource_helper.get_config', side_effect=['/'])

    result = ResourceHelper.get_agent_resource_path('test.txt', 1)

    assert result == '/test.txt'
