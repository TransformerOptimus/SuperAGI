import pytest
from unittest.mock import patch, Mock
from superagi.tools.code.run_code import RunCodeTool, RunCodeSchema
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution

class MockToolKit:
    session = Mock(spec_set=['_'])

class MockReturn:
    returncode = 0
    stderr = "MOCK_ERROR"
    stdout = "MOCK_OUTPUT"
    def __init__(self, **entries):
        self.__dict__.update(entries)

class MockReturn2:
    returncode = 1
    stderr = "MOCK_ERROR"
    stdout = "MOCK_OUTPUT"
    def __init__(self, **entries):
        self.__dict__.update(entries)

@pytest.fixture
def mock_tool():
    tool = RunCodeTool()
    tool.toolkit_config = MockToolKit()
    tool.agent_id = 1
    tool.agent_execution_id = 1

    return tool

@patch('subprocess.run', return_value=MockReturn())
@patch.object(Agent, 'get_agent_from_id')
@patch.object(AgentExecution, 'get_agent_execution_from_id')
@patch('superagi.tools.code.run_code.ResourceHelper.get_agent_read_resource_path')
def test_run_code_tool(mock_get_path, mock_get_execution, mock_get_agent, mock_run, mock_tool):
    mock_get_path.return_value = 'MOCK_PATH'
    mock_get_agent.return_value = Mock(spec_set=['_'])
    mock_get_execution.return_value = Mock(spec_set=['_'])

    res = mock_tool._execute('test_file.py')
    assert res == 'Result of running test_file.py : MOCK_OUTPUT'

    mock_get_path.assert_called_once_with('test_file.py', agent=mock_get_agent.return_value, agent_execution=mock_get_execution.return_value)
    mock_run.assert_called_once_with(["python", 'MOCK_PATH'], capture_output=True, text=True)

@patch('subprocess.run', return_value=MockReturn2())
@patch.object(Agent, 'get_agent_from_id')
@patch.object(AgentExecution, 'get_agent_execution_from_id')
@patch('superagi.tools.code.run_code.ResourceHelper.get_agent_read_resource_path')
def test_run_code_tool_fail(mock_get_path, mock_get_execution, mock_get_agent, mock_run, mock_tool):
    mock_get_path.return_value = 'MOCK_PATH'
    mock_get_agent.return_value = Mock(spec_set=['_'])
    mock_get_execution.return_value = Mock(spec_set=['_'])

    res = mock_tool._execute('test_file.py')
    assert res == 'An error occurred while running the script:\n\nMOCK_ERROR'
