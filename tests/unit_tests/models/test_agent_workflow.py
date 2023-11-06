import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from superagi.models.workflows.agent_workflow import AgentWorkflow


@pytest.fixture
def mock_session():
    session = MagicMock(spec=Session)
    session.query.return_value.filter.return_value.first.return_value = MagicMock(spec=AgentWorkflow)
    return session

def test_find_by_name(mock_session):
    result = AgentWorkflow.find_by_name(mock_session, 'workflow_name')
    mock_session.query.assert_called_once_with(AgentWorkflow)
    assert result.__class__ == AgentWorkflow

def test_find_or_create_by_name_new(mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None
    result = AgentWorkflow.find_or_create_by_name(mock_session, 'workflow_name', 'description')
    mock_session.add.assert_called_once()
    assert result.__class__ == AgentWorkflow

def test_find_or_create_by_name_exists(mock_session):
    result = AgentWorkflow.find_or_create_by_name(mock_session, 'workflow_name', 'description')
    mock_session.add.assert_not_called()
    assert result.__class__ == AgentWorkflow

def test_fetch_trigger_step_id(mock_session):
    result = AgentWorkflow.fetch_trigger_step_id(mock_session, 1)
    mock_session.query.assert_called_once()
    assert result is not None