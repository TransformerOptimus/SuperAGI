import pytest
from sqlalchemy.exc import SQLAlchemyError
from superagi.models.call_logs import CallLogs
from superagi.models.agent import Agent
from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit
from unittest.mock import MagicMock

from superagi.apm.call_log_helper import CallLogHelper

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_agent():
    return MagicMock()

@pytest.fixture
def mock_tool():
    return MagicMock()

@pytest.fixture
def mock_toolkit():
    return MagicMock()

@pytest.fixture
def call_log_helper(mock_session):
    return CallLogHelper(mock_session, 1)

def test_create_call_log_success(call_log_helper, mock_session):
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    call_log = call_log_helper.create_call_log('test', 1, 10, 'test_tool', 'test_model')

    assert isinstance(call_log, CallLogs)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_create_call_log_failure(call_log_helper, mock_session):
    mock_session.commit = MagicMock(side_effect=SQLAlchemyError())
    call_log = call_log_helper.create_call_log('test', 1, 10, 'test_tool', 'test_model')
    assert call_log is None

def test_fetch_data_success(call_log_helper, mock_session):
    mock_session.query = MagicMock()

    # creating mock results
    summary_result = (1, 1, 1)
    runs = [CallLogs(
        agent_execution_name='test',
        agent_id=1,
        tokens_consumed=10,
        tool_used='test_tool',
        model='test_model',
        org_id=1
    )]
    agents = [Agent(name='test_agent')]
    tools = [Tool(name='test_tool', toolkit_id=1)]
    toolkits = [Toolkit(name='test_toolkit')]

    # setup return values for the mock methods
    mock_session.query().filter().first.side_effect = [summary_result, runs, agents, toolkits, tools]

    result = call_log_helper.fetch_data('test_model')

    assert result is not None
    assert 'model' in result
    assert 'total_tokens' in result
    assert 'total_calls' in result
    assert 'total_agents' in result
    assert 'runs' in result

def test_fetch_data_failure(call_log_helper, mock_session):
    mock_session.query = MagicMock(side_effect=SQLAlchemyError())
    result = call_log_helper.fetch_data('test_model')

    assert result is None