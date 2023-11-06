import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from superagi.models.workflows.iteration_workflow_step import IterationWorkflowStep


@pytest.fixture
def mock_session():
    session = MagicMock(spec=Session)
    session.query.return_value.filter.return_value.first.return_value = MagicMock(spec=IterationWorkflowStep)
    return session


def test_find_by_id(mock_session):
    result = IterationWorkflowStep.find_by_id(mock_session, 1)
    mock_session.query.assert_called_once_with(IterationWorkflowStep)
    assert result.__class__ == IterationWorkflowStep


def test_find_or_create_step_new(mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None
    result = IterationWorkflowStep.find_or_create_step(mock_session, 1, 'unique_id', 'prompt', 'variables', 'step_type',
                                                       'output_type')
    mock_session.add.assert_called_once()
    assert result.__class__ == IterationWorkflowStep


def test_find_or_create_step_exists(mock_session):
    result = IterationWorkflowStep.find_or_create_step(mock_session, 1, 'unique_id', 'prompt', 'variables', 'step_type',
                                                       'output_type')
    mock_session.add.assert_not_called()
    assert result.__class__ == IterationWorkflowStep
