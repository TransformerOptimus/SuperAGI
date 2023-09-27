import pytest
from unittest.mock import Mock, patch
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.helper.error_handler import ErrorHandler

def test_handle_error():
    session = Mock()
    agent_id = 1
    agent_execution_id = 2
    error_message = 'Test error'
    
    mock_query = Mock()
    mock_query.filter().first.return_value = AgentExecution(id=agent_execution_id)
    session.query.return_value = mock_query

    ErrorHandler.handle_openai_errors(session, agent_id, agent_execution_id, error_message)

    session.query.assert_called_once_with(AgentExecution)
