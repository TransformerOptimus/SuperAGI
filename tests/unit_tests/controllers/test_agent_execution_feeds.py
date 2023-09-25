from unittest.mock import MagicMock, Mock, create_autospec, patch
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app
from fastapi_sqlalchemy import db
from superagi.controllers.agent_execution_feed import get_agent_execution_feed

@patch('superagi.controllers.agent_execution_feed.db')
def test_get_agent_execution_feed(mock_query):
    mock_session = create_autospec(pytest.Session)
    
    AgentExecution = MagicMock()
    agent_execution = AgentExecution()
    agent_execution.status = "PAUSED"
    agent_execution.last_shown_error_id = None
    
    AgentExecutionFeed = MagicMock()
    agent_execution_feed = AgentExecutionFeed()
    agent_execution_feed.error_message = None
    
    feeds = [agent_execution_feed]
    
    check_auth = MagicMock()
    AuthJWT = MagicMock()
    check_auth.return_value = AuthJWT  
    asc = MagicMock()
    
    AgentExecutionPermission = MagicMock()
    agent_execution_permission = AgentExecutionPermission()
    agent_execution_permission.id = 1
    agent_execution_permission.created_at = "2021-12-13T00:00:00"
    agent_execution_permission.response = "Yes"
    agent_execution_permission.status = "Completed"
    agent_execution_permission.tool_name = "Tool1"
    agent_execution_permission.question = "Question1"
    agent_execution_permission.user_feedback = "Feedback1"
        
    permissions = [agent_execution_permission]
    mock_agent_execution = Mock() 
    mock_query.return_value.filter.return_value.first.return_value = mock_agent_execution
    mock_agent_execution_id = 1
    assert get_agent_execution_feed(mock_agent_execution_id)