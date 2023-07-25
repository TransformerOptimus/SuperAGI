from unittest.mock import patch, MagicMock

from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.resource import Resource


def test_make_written_file_resource(mocker):
    mocker.patch('os.getcwd', return_value='/')
    mocker.patch('os.makedirs', return_value=None)
    mocker.patch('os.path.getsize', return_value=1000)
    mocker.patch('os.path.splitext', return_value=("", ".txt"))
    mocker.patch('superagi.helper.resource_helper.get_config', side_effect=['FILE', '/', '/', 'FILE'])
    mock_agent = Agent(id=1, name='TestAgent')
    mock_agent_execution = AgentExecution(id=1, name='TestExecution')
    session = MagicMock()

    with patch('superagi.helper.resource_helper.logger') as logger_mock:
        session.query.return_value.filter_by.return_value.first.return_value = None
        # Create a Resource object
        resource = Resource(
            name='test.txt',
            path='/test.txt',
            storage_type='FILE',
            size=1000,
            type='application/txt',
            channel='OUTPUT',
            agent_id=1,
            agent_execution_id=1
        )

        # Mock the session.add() method to return the created Resource object
        session.add.return_value = resource
        result = ResourceHelper.make_written_file_resource('test.txt', mock_agent, mock_agent_execution, session)

    assert result.name == 'test.txt'
    assert result.path == '/test.txt'
    assert result.storage_type == 'FILE'
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
    mock_agent = Agent(id=1, name='TestAgent')
    mock_agent_execution = AgentExecution(id=1, name='TestExecution')
    result = ResourceHelper.get_agent_write_resource_path('test.txt', mock_agent, mock_agent_execution)

    assert result == '/test.txt'


def test_get_formatted_agent_level_path():
    agent = Agent(id=1, name="TestAgent")
    path = "/data/{agent_id}/file.txt"
    formatted_path = ResourceHelper.get_formatted_agent_level_path(agent, path)
    expected_path = "/data/TestAgent_1/file.txt"
    assert formatted_path == expected_path


def test_get_formatted_agent_execution_level_path():
    agent_execution = AgentExecution(id=1, name="TestExecution")
    path = "/results/{agent_execution_id}/output.csv"
    formatted_path = ResourceHelper.get_formatted_agent_execution_level_path(agent_execution, path)
    expected_path = "/results/TestExecution_1/output.csv"
    assert formatted_path == expected_path
