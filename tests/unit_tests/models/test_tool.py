import pytest
from unittest.mock import MagicMock, call
from sqlalchemy.orm.exc import NoResultFound
from superagi.models.tool import Tool
from superagi.controllers.types.agent_with_config import AgentWithConfig
from fastapi import HTTPException
from typing import List

@pytest.fixture
def mock_session():
    session = MagicMock()
    get_mock = MagicMock()
    get_mock.side_effect = [MagicMock(), NoResultFound()]   # assuming 2nd tool won't be found
    session.query.return_value.get = get_mock
    return session

@pytest.fixture
def mock_agent_with_config():
    return AgentWithConfig(
        name="SmartAGI",
        project_id=1,
        description="AI assistant to solve complex problems",
        goal=["Share research on latest google news in fashion"],
        agent_type="Don't Maintain Task Queue",
        constraints=[
            "~4000 word limit for short term memory.",
            "Your short term memory is short, so immediately save important information to files.",
            "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
            "No user assistance",
            "Exclusively use the commands listed in double quotes e.g. \"command name\""
        ],
        instruction=[],
        toolkits=[10, 12],
        tools=[1,2],
        exit="Exit strategy",
        iteration_interval=500,
        model="gpt-4",
        permission_type="Type 1",
        LTM_DB="Database Pinecone",
        memory_window=10,
        max_iterations=25,
        user_timezone="Australia/Melbourne"
    )

def test_is_tool_id_valid_all_found(mock_session, mock_agent_with_config):
    # All tools found
    mock_session.query.return_value.get.side_effect = [MagicMock(), MagicMock()]  

    # Calls the is_tool_id_valid method and assert that it returns True
    assert Tool.is_tool_id_valid(mock_agent_with_config, mock_session) == True

    # assert that mock_session.query().get() was called with the correct arguments
    calls = [call(1), call(2)]
    mock_session.query.return_value.get.assert_has_calls(calls, any_order=True)

