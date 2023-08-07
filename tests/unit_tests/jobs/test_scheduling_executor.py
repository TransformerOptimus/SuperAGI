import pytest
from unittest.mock import patch, MagicMock, ANY, PropertyMock
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.jobs.scheduling_executor import ScheduledAgentExecutor
from datetime import datetime

@patch('superagi.worker.execute_agent.delay')
@patch('superagi.jobs.scheduling_executor.Session')
@patch('superagi.models.agent.Agent')
@patch('superagi.jobs.scheduling_executor.AgentWorkflow')
@patch('superagi.models.agent_execution.AgentExecution')
def test_execute_scheduled_agent(AgentExecutionMock, AgentWorkflowMock, AgentMock, SessionMock, execute_agent_delay_mock):
    # Arrange
    agent_id = 1
    name = 'Test Agent'

    # session setup
    session_mock = MagicMock()
    SessionMock.return_value = session_mock

    # agent setup
    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = agent_id
    session_mock.query.return_value.get.return_value = mock_agent

    db_agent_execution_mock = AgentExecution(status="RUNNING",last_execution_time=datetime.now(),agent_id=agent_id, name=name, num_of_calls=0, num_of_tokens=0, current_agent_step_id=1)
    type(db_agent_execution_mock).id = PropertyMock(return_value=123)
    AgentExecutionMock.return_value = db_agent_execution_mock

    # Create a ScheduledAgentExecutor object and then call execute_scheduled_agent
    executor = ScheduledAgentExecutor()
    
    # Act
    executor.execute_scheduled_agent(agent_id, name)


    # Assert
    assert session_mock.query.called
    assert session_mock.commit.called
    execute_agent_delay_mock.assert_called_once_with(db_agent_execution_mock.id, ANY)
    args, _ = execute_agent_delay_mock.call_args
    assert isinstance(args[0], int)
    assert isinstance(args[1], datetime)
