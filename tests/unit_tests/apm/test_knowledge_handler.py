import pytest
from unittest.mock import MagicMock
from superagi.apm.knowledge_handler import KnowledgeHandler
from fastapi import HTTPException
from datetime import datetime
import pytz

@pytest.fixture
def organisation_id():
    return 1

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def knowledge_handler(mock_session, organisation_id):
    return KnowledgeHandler(mock_session, organisation_id)

def test_get_knowledge_usage_by_name(knowledge_handler, mock_session):
    knowledge_handler.session = mock_session
    knowledge_name = 'Knowledge1'
    mock_knowledge_event = MagicMock()
    mock_knowledge_event.knowledge_unique_agents = 5
    mock_knowledge_event.knowledge_name = knowledge_name
    mock_knowledge_event.id = 1

    mock_session.query.return_value.filter_by.return_value.filter.return_value.first.return_value = mock_knowledge_event
    mock_session.query.return_value.filter.return_value.group_by.return_value.first.return_value = mock_knowledge_event
    mock_session.query.return_value.filter.return_value.count.return_value = 10

    result = knowledge_handler.get_knowledge_usage_by_name(knowledge_name)

    assert isinstance(result, dict)
    assert result == {
        'knowledge_unique_agents': 5,
        'knowledge_calls': 10
    }

    mock_session.query.return_value.filter_by.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException):
        knowledge_handler.get_knowledge_usage_by_name('NonexistentKnowledge')

def test_get_knowledge_events_by_name(knowledge_handler, mock_session):
    knowledge_name = 'knowledge1'
    knowledge_handler.session = mock_session
    knowledge_handler.organisation_id = 1

    mock_knowledge = MagicMock()
    mock_knowledge.id = 1
    mock_session.query().filter_by().filter().first.return_value = mock_knowledge

    result_obj = MagicMock()
    result_obj.agent_id = 1
    result_obj.created_at = datetime.now()
    result_obj.event_name = 'knowledge_picked'
    result_obj.event_property = {'knowledge_name': 'knowledge1', 'agent_execution_id': '1'}
    result_obj2 = MagicMock()
    result_obj2.agent_id = 1
    result_obj2.event_name = 'run_completed'
    result_obj2.event_property = {'tokens_consumed': 10, 'calls': 5, 'name': 'Runner', 'agent_execution_id': '1'}
    result_obj3 = MagicMock()
    result_obj3.agent_id = 1
    result_obj3.event_name = 'agent_created'
    result_obj3.event_property = {'agent_name': 'A1', 'model': 'M1'}

    mock_session.query().filter().all.side_effect = [[result_obj], [result_obj2], [result_obj3]]
    
    user_timezone = MagicMock()
    user_timezone.value = 'America/New_York'
    mock_session.query().filter().first.return_value = user_timezone
    
    result = knowledge_handler.get_knowledge_events_by_name(knowledge_name)

    assert isinstance(result, list)
    assert len(result) == 1
    for item in result:
        assert 'agent_execution_id' in item
        assert 'created_at' in item
        assert 'tokens_consumed' in item
        assert 'calls' in item
        assert 'agent_execution_name' in item
        assert 'agent_name' in item
        assert 'model' in item


def test_get_knowledge_events_by_name_knowledge_not_found(knowledge_handler, mock_session):
    knowledge_name = "knowledge1"
    not_found_message = 'Knowledge not found'

    mock_session.query().filter_by().filter().first.return_value = None

    try:
        knowledge_handler.get_knowledge_events_by_name(knowledge_name)
        assert False, "Expected HTTPException has not been raised"
    except HTTPException as e:
        assert str(e.detail) == not_found_message, f"Expected {not_found_message}, got {e.detail}"
    finally:
        assert mock_session.query().filter_by().filter().first.called, "first() function not called"