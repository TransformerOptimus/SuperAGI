import pytest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from superagi.agent.common_types import ToolExecutorResponse
from superagi.agent.tool_executor import ToolExecutor

class MockTool:
    def __init__(self, name):
        self.name = name

    def execute(self, args):
        return self.name

@pytest.fixture
def mock_tools():
    return [MockTool(name=f'tool{i}') for i in range(5)]

@pytest.fixture
def executor(mock_tools):
    return ToolExecutor(organisation_id=1, agent_id=1, tools=mock_tools)

def test_tool_executor_finish(executor):
    res = executor.execute(None, 'finish', {})
    assert res.status == 'COMPLETE'
    assert res.result == ''

@patch('superagi.agent.tool_executor.EventHandler')
def test_tool_executor_success(mock_event_handler, executor, mock_tools):
    for i, tool in enumerate(mock_tools):
        res = executor.execute(None, f'tool{i}', {})
        assert res.status == 'SUCCESS'
        assert res.result == f'Tool {tool.name} returned: {tool.name}'
        assert res.retry == False

@patch('superagi.agent.tool_executor.EventHandler')
def test_tool_executor_generic_error(mock_event_handler, executor):
    tool = MockTool('error_tool')
    tool.execute = Mock(side_effect=Exception('generic error'))
    executor.tools.append(tool)

    res = executor.execute(None, 'error_tool', {})
    assert res.status == 'ERROR'
    assert 'Error1: generic error' in res.result
    assert res.retry == True

def test_tool_executor_unknown_tool(executor):
    res = executor.execute(None, 'unknown_tool', {})
    assert res.status == 'ERROR'
    assert "Unknown tool 'unknown_tool'" in res.result
    assert res.retry == True

def test_clean_tool_args(executor):
    args = {"arg1": {"value": 1}, "arg2": 2}
    clean_args = executor.clean_tool_args(args)
    assert clean_args == {"arg1": 1, "arg2": 2}