import pytest
from unittest.mock import MagicMock
from superagi.apm.knowledge_handler import KnowledgeHandler
from fastapi import HTTPException

@pytest.fixture
def organisation_id():
    return 1

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def knowledge_handler(mock_session, organisation_id):
    return KnowledgeHandler(mock_session, organisation_id)

def test_get_knowledge_wise_usage(knowledge_handler, mock_session):
    knowledge_handler.session = mock_session
    mock_knowledge_event = MagicMock()
    mock_knowledge_event.knowledge_name = 'Knowledge1'
    mock_knowledge_event.knowledge_unique_agents = 5

    mock_session.query.return_value.filter.return_value.group_by.return_value.all.return_value = [mock_knowledge_event]
    mock_session.query.return_value.filter.return_value.count.return_value = 10

    result = knowledge_handler.get_knowledge_wise_usage()

    assert isinstance(result, dict)
    assert result == {
        'Knowledge1': {
            'knowledge_unique_agents': 5,
            'knowledge_calls': 10
        }
    }

def test_get_knowledge_events_by_name(knowledge_handler, mock_session):
    knowledge_name = 'knowledge1'
    knowledge_handler.session = mock_session

    mock_knowledge = MagicMock()
    mock_knowledge.name = 'knowledge1'
    mock_session.query().filter_by().first.return_value = mock_knowledge

    result_obj = MagicMock()
    result_obj.agent_id = 1
    result_obj.created_at = "2022-05-25"
    result_obj.event_name = 'knowledge_picked'
    result_obj.tokens_consumed = 10
    result_obj.calls = 5
    result_obj.agent_execution_name = 'Runner'
    result_obj.agent_name = 'A1'
    result_obj.model = 'M1'

    mock_subquery = MagicMock()
    mock_subquery.c.agent_id = 1

    mock_session.query().filter().group_by().subquery.return_value = mock_subquery
    mock_session.query().join().join().join().all.return_value = [result_obj]
    
    result = knowledge_handler.get_knowledge_events_by_name(knowledge_name)

    assert isinstance(result, list)
    expected_result = [{
        'agent_id': 1,
        'created_at': '2022-05-25',
        'event_name': 'knowledge_picked',
        'tokens_consumed': 10,
        'calls': 5,
        'agent_execution_name': 'Runner',
        'agent_name': 'A1',
        'model': 'M1'
    }]
    assert result == expected_result

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
