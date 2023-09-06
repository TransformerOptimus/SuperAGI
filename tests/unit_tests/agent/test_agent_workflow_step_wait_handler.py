from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from superagi.models.agent_execution import AgentExecution
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.agent.agent_workflow_step_wait_handler import AgentWaitStepHandler


# Mock datetime.now() for testing
@pytest.fixture
def mock_datetime_now():
    return datetime(2023, 9, 6, 12, 0, 0)


@pytest.fixture(autouse=True)
def mock_datetime_now_fixture(monkeypatch, mock_datetime_now):
    monkeypatch.setattr("superagi.agent.agent_workflow_step_wait_handler.datetime",
                        MagicMock(now=MagicMock(return_value=mock_datetime_now)))

# Test cases
@patch.object(AgentExecution, 'get_agent_execution_from_id')
@patch.object(AgentWorkflowStep, 'find_by_id')
@patch.object(AgentWorkflowStep, 'fetch_next_step')
def test_handle_next_step_complete(mock_fetch_next_step, mock_find_by_id, mock_get_agent_execution_from_id, mock_datetime_now_fixture):
    mock_session = MagicMock()
    mock_agent_execution = MagicMock(current_agent_step_id=1, status="WAIT_STEP")

    mock_get_agent_execution_from_id.return_value = mock_agent_execution
    mock_find_by_id.return_value = MagicMock()

    mock_next_step = MagicMock(id=2)
    mock_next_step.__str__.return_value = "COMPLETE"
    mock_fetch_next_step.return_value = mock_next_step

    handler = AgentWaitStepHandler(mock_session, 1, 2)

    handler.handle_next_step()

    # Assertions
    assert mock_agent_execution.current_agent_step_id == -1
    assert mock_agent_execution.status == "COMPLETED"
    mock_session.commit.assert_called_once()


# Test cases
@patch.object(AgentExecution, 'get_agent_execution_from_id')
@patch.object(AgentWorkflowStep, 'find_by_id')
@patch.object(AgentWorkflowStep, 'fetch_next_step')
def test_execute_step(mock_fetch_next_step, mock_find_by_id, mock_get_agent_execution_from_id):
    mock_session = MagicMock()
    mock_agent_execution = MagicMock(current_agent_step_id=1, status="WAIT_STEP")
    mock_step_wait = MagicMock(status="WAITING")

    mock_get_agent_execution_from_id.return_value = mock_agent_execution
    mock_find_by_id.return_value = mock_step_wait
    mock_fetch_next_step.return_value = MagicMock()

    handler = AgentWaitStepHandler(mock_session, 1, 2)

    handler.execute_step()

    # Assertions
    assert mock_step_wait.status == "WAITING"
    assert mock_agent_execution.status == "WAIT_STEP"
    mock_session.commit.assert_called_once()