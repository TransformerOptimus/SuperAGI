import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from superagi.apm.tools_handler import ToolsHandler
from sqlalchemy.orm import Session
from datetime import datetime
import pytz

@pytest.fixture
def organisation_id():
    return 1

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def tools_handler(mock_session, organisation_id):
    return ToolsHandler(mock_session, organisation_id)

def test_calculate_tool_usage(tools_handler, mock_session):
    tool_used_subquery = MagicMock()
    agent_count_subquery = MagicMock()
    total_usage_subquery = MagicMock()

    tool_used_subquery.c.tool_name = 'Tool1'
    tool_used_subquery.c.agent_id = 1

    agent_count_subquery.c.tool_name = 'Tool1'
    agent_count_subquery.c.unique_agents = 1

    total_usage_subquery.c.tool_name = 'Tool1'
    total_usage_subquery.c.total_usage = 5

    tools_handler.get_tool_and_toolkit = MagicMock()
    tools_handler.get_tool_and_toolkit.return_value = {'Tool1': 'Toolkit1'}

    mock_session.query().filter_by().subquery.return_value = tool_used_subquery
    mock_session.query().group_by().subquery.return_value = agent_count_subquery
    mock_session.query().group_by().subquery.return_value = total_usage_subquery

    result_obj = MagicMock()
    result_obj.tool_name = 'Tool1'
    result_obj.unique_agents = 1
    result_obj.total_usage = 5
    mock_session.query().join().all.return_value = [result_obj]

    result = tools_handler.calculate_tool_usage()

    assert isinstance(result, list)

    expected_output = [{'tool_name': 'Tool1', 'unique_agents': 1, 'total_usage': 5, 'toolkit': 'Toolkit1'}]
    assert result == expected_output

def test_get_tool_and_toolkit(tools_handler, mock_session):
    result_obj = MagicMock()
    result_obj.tool_name = 'tool 1'
    result_obj.toolkit_name = 'toolkit 1'
    
    mock_session.query().join().all.return_value = [result_obj]
    
    output = tools_handler.get_tool_and_toolkit()
    
    assert isinstance(output, dict)
    assert output == {'tool 1': 'toolkit 1'} 

def test_get_tool_wise_usage(tools_handler, mock_session):
    tools_handler.session = mock_session
    mock_tool_event = MagicMock()
    mock_tool_event.tool_name = 'Tool1'
    mock_tool_event.tool_calls = 10
    mock_tool_event.tool_unique_agents = 5

    mock_session.query.return_value.filter.return_value.group_by.return_value = [mock_tool_event]
    result = tools_handler.get_tool_wise_usage()

    assert isinstance(result, dict)
    assert result == {
        'Tool1': {
            'tool_calls': 10,
            'tool_unique_agents': 5
        }
    }

def test_get_tool_events_by_name(tools_handler, mock_session):
    tool_name = 'tool1'

    mock_tool = MagicMock()
    mock_tool.name = "tool1"
    mock_session.query().filter_by().first.return_value = mock_tool

    result_obj = MagicMock()
    result_obj.agent_id = 1
    result_obj.created_at = datetime.now()  # Set created_at to datetime not string
    result_obj.event_name = 'tool_used'
    result_obj.tokens_consumed = 10
    result_obj.calls = 5
    result_obj.agent_execution_name = 'Runner'
    result_obj.agent_name = 'A1'
    result_obj.model = 'M1'
    result_obj.other_tools = ['tool2', 'tool3']

    user_timezone = MagicMock()
    user_timezone.value = 'UTC'
    mock_session.query().filter().first.return_value = user_timezone

    mock_session.query().join().join().join().join().all.return_value = [result_obj]
    result = tools_handler.get_tool_events_by_name(tool_name)

    assert isinstance(result, list)

    expected_result = [{
        'agent_id': 1,
        'created_at': result_obj.created_at.astimezone(pytz.timezone(user_timezone.value)).strftime("%d %B %Y %H:%M"),
        'event_name': 'tool_used',
        'tokens_consumed': 10,
        'calls': 5,
        'agent_execution_name': 'Runner',
        'agent_name': 'A1',
        'model': 'M1',
        'other_tools': ['tool2', 'tool3']
    }]
    assert result == expected_result

def test_get_tool_events_by_name_tool_not_found(tools_handler, mock_session):
    tool_name = "tool1"
    
    mock_session.query().filter_by().first.return_value = None
    with pytest.raises(HTTPException):
        tools_handler.get_tool_events_by_name(tool_name)
        
    assert mock_session.query().filter_by().first.called