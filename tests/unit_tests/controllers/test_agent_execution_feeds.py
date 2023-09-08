import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException
from superagi.controllers.agent_execution_feed import get_agent_execution_feed
from superagi.models.agent_execution import AgentExecution

@patch('superagi.controllers.agent_execution_feed.db')
def test_get_agent_execution_feed(mock_query):
   
   
    # Return a Mock object for the AgentExecution
    mock_agent_execution = Mock() 
    mock_query.return_value.filter.return_value.first.return_value = mock_agent_execution
    mock_agent_execution_id = 1
    assert get_agent_execution_feed(mock_agent_execution_id) 

