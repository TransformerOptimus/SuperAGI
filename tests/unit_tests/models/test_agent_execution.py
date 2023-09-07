from datetime import datetime
from unittest.mock import create_autospec, patch, Mock

import pytest
from pytest_mock import mocker
from sqlalchemy.orm import Session

from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.iteration_workflow import IterationWorkflow
def test_get_agent_execution_from_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample agent ID
    agent_execution_id = 1

    # Create a mock agent execution object to be returned by the session query
    mock_agent_execution = AgentExecution(id=agent_execution_id, name="Test Execution")

    # Configure the session query to return the mock agent
    session.query.return_value.filter.return_value.first.return_value = mock_agent_execution

    # Call the method under test
    agent = AgentExecution.get_agent_execution_from_id(session, agent_execution_id)

    # Assert that the returned agent object matches the mock agent
    assert agent == mock_agent_execution



@pytest.fixture
def mock_session(mocker):
    # Create a mock for the session object
    mock_session = mocker.Mock()
    return mock_session


def test_update_tokens(mock_session):
    # Create a mock agent execution
    mock_execution = AgentExecution(
        id=1,
        status='RUNNING',
        name='Agent',
        agent_id=1,
        last_execution_time=datetime.now(),
        num_of_calls=1,
        num_of_tokens=100,
        current_agent_step_id=1
    )

    # Mock the query response
    mock_session.query.return_value.filter.return_value.first.return_value = mock_execution

    # Call the method
    AgentExecution.update_tokens(mock_session, 1, 50)

    # Check that the attributes were updated
    assert mock_execution.num_of_calls == 2
    assert mock_execution.num_of_tokens == 150


def test_assign_next_step_id(mock_session, mocker):
    # Create a mock agent execution and workflow step
    mock_execution = AgentExecution(
        id=1,
        status='RUNNING',
        name='Agent',
        agent_id=1,
        last_execution_time=datetime.now(),
        num_of_calls=1,
        num_of_tokens=100,
        current_agent_step_id=1
    )
    mock_step = AgentWorkflowStep(id=2, action_type='ITERATION_WORKFLOW', action_reference_id=1)
    mock_trigger_step = IterationWorkflow(id=3)

    # Mock the query responses
    mock_session.query.return_value.filter.return_value.first.return_value = mock_execution
    mocker.patch.object(AgentWorkflowStep, 'find_by_id', return_value=mock_step)
    mocker.patch.object(IterationWorkflow, 'fetch_trigger_step_id', return_value=mock_trigger_step)

    # Call the method
    AgentExecution.assign_next_step_id(mock_session, 1, 2)

    # Check that the attributes were updated
    assert mock_execution.current_agent_step_id == 2
    assert mock_execution.iteration_workflow_step_id == 3

def test_get_execution_by_agent_id_and_status():
    session = create_autospec(Session)

    # Create a sample agent execution ID
    agent_execution_id = 1

    # Create a mock agent execution object to be returned by the session query
    mock_agent_execution = AgentExecution(id=agent_execution_id, name="Test Execution", status="RUNNING")

    # Configure the session query to return the mock agent
    session.query.return_value.filter.return_value.first.return_value = mock_agent_execution

    # Call the method under test
    agent_execution = AgentExecution.get_execution_by_agent_id_and_status(session, agent_execution_id,"RUNNING")

    # Assert that the returned agent object matches the mock agent
    assert agent_execution == mock_agent_execution
    assert agent_execution.status == "RUNNING"

@pytest.fixture
def mock_session(mocker):
    return mocker.MagicMock()


