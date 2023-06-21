import pytest
from unittest.mock import patch
from superagi.helper.resource_helper import ResourceHelper  # Replace with actual import
@pytest.fixture
def resource_helper():
    with patch('superagi.helper.resource_helper.get_config') as get_config_mock, \
         patch('superagi.helper.resource_helper.os.getcwd') as get_cwd_mock, \
         patch('superagi.helper.resource_helper.os.path.getsize') as getsize_mock:

        get_config_mock.return_value = '/fake/path'
        get_cwd_mock.return_value = '/fake/cwd'
        getsize_mock.return_value = 100

        yield

def test_make_written_file_resource(resource_helper):
    file_name = 'test.png'
    agent_id = 1
    channel = 'INPUT'
    result = ResourceHelper.make_written_file_resource(file_name, agent_id, channel)

    assert result.name == file_name
    assert result.path == '/fake/path/' + file_name
    assert result.size == 100
    assert result.type == 'image/png'
    assert result.channel == 'OUTPUT'
    assert result.agent_id == agent_id

def test_get_resource_path(resource_helper):
    file_name = 'test.png'
    result = ResourceHelper.get_resource_path(file_name)

    assert result == '/fake/path/test.png'
