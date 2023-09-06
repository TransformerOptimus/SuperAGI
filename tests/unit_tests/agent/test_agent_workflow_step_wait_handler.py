from datetime import datetime
from unittest.mock import MagicMock

import pytest

from superagi.models.agent_execution import AgentExecution
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def mock_agent_execution():
    return MagicMock()


@pytest.fixture
def mock_workflow_step():
    return MagicMock()

@pytest.fixture
def mock_step_wait():
    return MagicMock()


# Mock datetime.now() for testing
@pytest.fixture
def mock_datetime_now():
    return datetime(2023, 9, 6, 12, 0, 0)

from superagi.agent.agent_workflow_step_wait_handler import AgentWaitStepHandler

@pytest.fixture(autouse=True)
def mock_datetime_now_fixture(monkeypatch, mock_datetime_now):
    monkeypatch.setattr("superagi.agent.agent_workflow_step_wait_handler.datetime",
                        MagicMock(now=MagicMock(return_value=mock_datetime_now)))


# Test cases
def test_handle_next_step_complete(mock_session, mock_agent_execution, mock_workflow_step):
    mock_agent_execution.get_agent_execution_from_id.return_value = mock_agent_execution
    mock_workflow_step.find_by_id.return_value = mock_workflow_step
    mock_agent_execution.current_agent_step_id = 1
    mock_agent_execution.status = "WAIT_STEP"

    mock_next_step = MagicMock(id=2)
    mock_next_step.__str__.return_value = "COMPLETE"
    mock_workflow_step.fetch_next_step.return_value = mock_next_step

    handler = AgentWaitStepHandler(mock_session, 1, 2)

    handler.handle_next_step()

    # Assertions
    assert mock_agent_execution.current_agent_step_id == -1
    assert mock_agent_execution.status == "COMPLETED"
    mock_session.commit.assert_called_once()

def test_handle_next_step_complete(mock_session, mock_agent_execution, mock_workflow_step):
    mock_agent_execution.get_agent_execution_from_id.return_value = mock_agent_execution
    mock_workflow_step.find_by_id.return_value = mock_workflow_step
    mock_agent_execution.current_agent_step_id = 1
    mock_agent_execution.status = "COMPLETED"

    mock_next_step = MagicMock(id=2)
    mock_next_step.__str__.return_value = "COMPLETE"
    mock_workflow_step.fetch_next_step.return_value = mock_next_step

    AgentWorkflowStep.fetch_next_step = MagicMock(return_value="COMPLETE")
    AgentExecution.assign_next_step_id = MagicMock()

    handler = AgentWaitStepHandler(mock_session, 1, 2)

    handler.handle_next_step()

    # Assertions
    assert mock_agent_execution.current_agent_step_id == 1
    assert mock_agent_execution.status == "COMPLETED"
    mock_session.commit.assert_called_once()

# Test cases
def test_execute_step(mock_session, mock_agent_execution, mock_workflow_step, mock_step_wait):
    mock_agent_execution.get_agent_execution_from_id.return_value = mock_agent_execution
    mock_workflow_step.find_by_id.return_value = mock_workflow_step
    mock_step_wait.find_by_id.return_value = mock_step_wait

    mock_step_wait.status = "WAITING"
    mock_agent_execution.status = "WAIT_STEP"
    handler = AgentWaitStepHandler(mock_session, 1, 2)

    handler.execute_step()

    # Assertions
    assert mock_step_wait.status == "WAITING"
    assert mock_agent_execution.status == "WAIT_STEP"
    mock_session.commit.assert_called_once()
