from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from superagi.models.workflows.iteration_workflow import IterationWorkflow

@patch('sqlalchemy.orm.Session.query')
def test_find_by_id(mock_query):
    mock_query.return_value.filter.return_value.first.return_value = MagicMock(spec=IterationWorkflow)
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = IterationWorkflow.find_by_id(session, 1)
    mock_query.assert_called_once_with(IterationWorkflow)
    assert result.__class__ == IterationWorkflow

@patch('sqlalchemy.orm.Session.query')
def test_find_workflow_by_name(mock_query):
    mock_query.return_value.filter.return_value.first.return_value = MagicMock(spec=IterationWorkflow)
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = IterationWorkflow.find_workflow_by_name(session, 'workflow_name')
    mock_query.assert_called_once_with(IterationWorkflow)
    assert result.__class__ == IterationWorkflow

@patch('sqlalchemy.orm.Session.add')
@patch('sqlalchemy.orm.Session.query')
def test_find_or_create_by_name_new(mock_query, mock_add):
    mock_query.return_value.filter.return_value.first.return_value = None
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = IterationWorkflow.find_or_create_by_name(session, 'workflow_name', 'description', False)
    assert result.__class__ == IterationWorkflow

@patch('sqlalchemy.orm.Session.add')
@patch('sqlalchemy.orm.Session.query')
def test_find_or_create_by_name_exists(mock_query, mock_add):
    mock_query.return_value.filter.return_value.first.return_value = MagicMock(spec=IterationWorkflow)
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = IterationWorkflow.find_or_create_by_name(session, 'workflow_name', 'description', False)
    mock_add.assert_not_called()
    assert result.__class__ == IterationWorkflow

@patch('sqlalchemy.orm.Session.query')
def test_fetch_trigger_step_id(mock_query):
    mock_query.return_value.filter.return_value.first.return_value = MagicMock()  # Assume we have a proper trigger step
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = IterationWorkflow.fetch_trigger_step_id(session, 1)
    mock_query.assert_called_once()  # The mock_query must be called once
    assert result is not None