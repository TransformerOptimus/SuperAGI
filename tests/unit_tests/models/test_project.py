import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm.exc import NoResultFound
from superagi.models.project import Project
from superagi.controllers.types.agent_with_config import AgentWithConfig
from fastapi import HTTPException

@pytest.fixture
def mock_session():
    session = MagicMock()
    get_mock = MagicMock()
    get_mock.side_effect = [MagicMock(), NoResultFound()]  # project not found on second call
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
            "~4000 word limit for short term memory."
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

def test_get_project_from_project_id_project_found(mock_session, mock_agent_with_config):
    Project.get_project_from_project_id(mock_agent_with_config, mock_session)
    mock_session.query.return_value.get.assert_called_once_with(mock_agent_with_config.project_id)