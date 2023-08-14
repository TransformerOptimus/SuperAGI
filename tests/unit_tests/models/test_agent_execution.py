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

def test_get_all_executions_by_status_and_agent_id():
    session = create_autospec(Session)

    # Create a sample agent execution ID and agent ID
    agent_id = 1
    execution_state_change_input = Mock(run_ids=[1, 2, 3])

    # Create mock agent execution objects
    mock_agent_execution_1 = AgentExecution(id=1, agent_id=agent_id, status="RUNNING")
    mock_agent_execution_2 = AgentExecution(id=2, agent_id=agent_id, status="RUNNING")
    mock_agent_execution_3 = AgentExecution(id=3, agent_id=agent_id, status="RUNNING")

    # Configure the session query to return the mock agent executions
    session.query().filter().all.return_value = [mock_agent_execution_1, mock_agent_execution_2, mock_agent_execution_3]

    # Call the method under test
    result = AgentExecution.get_all_executions_by_status_and_agent_id(
        session, agent_id, execution_state_change_input, "RUNNING"
    )

    # Assert that the returned execution objects match the mock agent executions
    assert result == [mock_agent_execution_1, mock_agent_execution_2, mock_agent_execution_3]
    assert result[0].status == "RUNNING"
    assert result[1].status == "RUNNING"
    assert result[2].status == "RUNNING"

@pytest.fixture
def mock_session(mocker):
    return mocker.MagicMock()

def test_get_all_executions_by_filter_config_with_run_ids(mock_session):
    # Create a mock session and setup its query method to return expected values
    mock_query = mock_session.query.return_value.filter.return_value
    mock_query.filter.return_value.all.return_value = [
        Mock(id=1, agent_id=1, status="CREATED"),
        Mock(id=2, agent_id=1, status="RUNNING"),
    ]

    # Create a mock filter configuration with run_ids
    mock_filter_config = Mock(run_ids=[1, 2])

    # Call the function with the mock filter configuration
    agent_id = 1
    result = AgentExecution.get_all_executions_by_filter_config(mock_session, agent_id, mock_filter_config)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2

def test_validate_run_ids_invalid(mock_session):
    mock_session.query.return_value.filter.return_value.distinct.return_value.all.side_effect = [
        [(1,), (2,)],  # agent_ids
        [(10,), (20,)],  # project_ids
        [(100,)],  # org_ids
    ]

    # Call the function with invalid parameters
    run_ids = [10, 20]
    organisation_id = 200
    with pytest.raises(Exception, match="one or more run IDs not found"):
        AgentExecution.validate_run_ids(mock_session, run_ids, organisation_id)


def test_validate_run_ids_valid(mock_session):
    # Create a mock session and setup its query method to return expected values
    mock_session.query.return_value.filter.return_value.distinct.return_value.all.side_effect = [
        [(1,), (2,)],  # agent_ids
        [(10,), (20,)],  # project_ids
        [(100,)],  # org_ids
    ]

    # Call the function with valid parameters
    run_ids = [1, 2]
    organisation_id = 100

    # The function should not raise an exception
    AgentExecution.validate_run_ids(mock_session, run_ids, organisation_id)