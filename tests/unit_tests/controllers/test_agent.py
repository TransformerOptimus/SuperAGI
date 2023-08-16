from unittest.mock import patch, Mock
from unittest import mock
import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.models.agent_schedule import AgentSchedule
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent import Agent
from datetime import datetime, timedelta
from pytz import timezone

client = TestClient(app)

@pytest.fixture
def mock_patch_schedule_input():
    return{
        "agent_id": 1,
        "start_time": "2023-02-02 01:00:00",
        "recurrence_interval": "2 Hours",
        "expiry_date": "2023-12-30 01:00:00",
        "expiry_runs": -1
    }

@pytest.fixture
def mock_schedule():
    # Mock schedule data for testing
    return AgentSchedule(id=1, agent_id=1, status="SCHEDULED")

@pytest.fixture
def mock_agent_config():
    return AgentConfiguration(key="user_timezone", agent_id=1, value='GMT')

@pytest.fixture
def mock_schedule_get():
    return AgentSchedule(
        id=1, 
        agent_id=1, 
        status="SCHEDULED",
        start_time= datetime(2022, 1, 1, 10, 30),
        recurrence_interval="5 Minutes",
        expiry_date=datetime(2022, 1, 1, 10, 30) + timedelta(days=10),
        expiry_runs=5 
    )

'''Test for Stopping Agent Scheduling'''
def test_stop_schedule_success(mock_schedule):
    with patch('superagi.controllers.agent.db') as mock_db:
        # Set up the database query result
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_schedule 

        # Call the endpoint
        response = client.post("agents/stop/schedule?agent_id=1")

        # Verify the HTTP response
        assert response.status_code == 200

        # Verify changes in the mock agent schedule
        assert mock_schedule.status == "STOPPED"


def test_stop_schedule_not_found():
    with patch('superagi.controllers.agent.db') as mock_db:
        # Set up the database query result
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        # Call the endpoint
        response = client.post("agents/stop/schedule?agent_id=1")

        # Verify the HTTP response
        assert response.status_code == 404
        assert response.json() == {"detail": "Schedule not found"}


'''Test for editing agent schedule'''
def test_edit_schedule_success(mock_schedule, mock_patch_schedule_input):
    with patch('superagi.controllers.agent.db') as mock_db:
        # Set up the database query result
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_schedule

        # Call the endpoint
        response = client.put("agents/edit/schedule", json=mock_patch_schedule_input)

        # Verify the HTTP response
        assert response.status_code == 200
        start_time = datetime.strptime(mock_patch_schedule_input["start_time"], "%Y-%m-%d %H:%M:%S")
        expiry_date = datetime.strptime(mock_patch_schedule_input["expiry_date"], "%Y-%m-%d %H:%M:%S")

        # Verify changes in the mock agent schedule
        assert mock_schedule.start_time == start_time
        assert mock_schedule.recurrence_interval == mock_patch_schedule_input["recurrence_interval"]
        assert mock_schedule.expiry_date == expiry_date
        assert mock_schedule.expiry_runs == mock_patch_schedule_input["expiry_runs"]


def test_edit_schedule_not_found(mock_patch_schedule_input):
    with patch('superagi.controllers.agent.db') as mock_db:
        # Set up the database query result
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        # Call the endpoint
        response = client.put("agents/edit/schedule", json=mock_patch_schedule_input)

        # Verify the HTTP response
        assert response.status_code == 404
        assert response.json() == {"detail": "Schedule not found"}

'''Test for getting agent schedule'''
def test_get_schedule_data_success(mock_schedule_get, mock_agent_config):
    with patch('superagi.controllers.agent.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.first.side_effect = [mock_schedule_get, mock_agent_config]
        response = client.get("agents/get/schedule_data/1")
        assert response.status_code == 200

        time_gmt = mock_schedule_get.start_time.astimezone(timezone('GMT'))

        expected_data = {
            "current_datetime": mock.ANY,
            "start_date": time_gmt.strftime("%d %b %Y"),
            "start_time": time_gmt.strftime("%I:%M %p"),
            "recurrence_interval": mock_schedule_get.recurrence_interval,
            "expiry_date": mock_schedule_get.expiry_date.astimezone(timezone('GMT')).strftime("%d/%m/%Y"),
            "expiry_runs": mock_schedule_get.expiry_runs,
        }
        assert response.json() == expected_data


def test_get_schedule_data_not_found():
    with patch('superagi.controllers.agent.db') as mock_db:
        # Set up the database query result
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        # Call the endpoint
        response = client.get("agents/get/schedule_data/1")

        # Verify the HTTP response
        assert response.status_code == 404
        assert response.json() == {"detail": "Agent Schedule not found"}


@pytest.fixture
def mock_agent_config_schedule():
    return {
        "agent_config": {
            "name": "SmartAGI", 
            "project_id": 1,
            "description": "AI assistant to solve complex problems",
            "goal": ["Share research on latest google news in fashion"],
            "agent_workflow": "Don't Maintain Task Queue",
            "constraints": [
                "~4000 word limit for short term memory.",
                "No user assistance",
                "Exclusively use the commands listed in double quotes"
            ],
            "instruction": [],
            "exit": "Exit strategy",
            "iteration_interval": 500,
            "model": "gpt-4",
            "permission_type": "Type 1",
            "LTM_DB": "Database Pinecone",
            "toolkits": [1],
            "tools": [],
            "memory_window": 10,
            "max_iterations": 25,
            "user_timezone": "Asia/Kolkata"
        },
        "schedule": {
            "start_time": "2023-07-04 11:13:00",
            "expiry_runs": -1,
            "recurrence_interval": None,
            "expiry_date": None
        }
    }

@pytest.fixture
def mock_agent():
    agent = Agent(id=1, name="SmartAGI", project_id=1)
    return agent


def test_create_and_schedule_agent_success(mock_agent_config_schedule, mock_agent, mock_schedule):
    
    with patch('superagi.models.agent.Agent') as AgentMock,\
         patch('superagi.controllers.agent.Project') as ProjectMock,\
         patch('superagi.controllers.agent.Tool') as ToolMock,\
         patch('superagi.controllers.agent.Toolkit') as ToolkitMock,\
         patch('superagi.controllers.agent.AgentSchedule') as AgentScheduleMock,\
         patch('superagi.controllers.agent.db') as db_mock:

        project_mock = Mock()
        ProjectMock.get.return_value = project_mock

        # AgentMock.create_agent_with_config.return_value = mock_agent
        AgentMock.return_value =  mock_agent

        tool_mock = Mock()
        ToolMock.get_invalid_tools.return_value = []

        toolkit_mock = Mock()
        ToolkitMock.fetch_tool_ids_from_toolkit.return_value = []
        
        agent_schedule_mock = Mock()
        agent_schedule_mock.id = None  # id is None before commit
        AgentScheduleMock.return_value = mock_schedule
        
        db_mock.session.query.return_value.get.return_value = project_mock
        db_mock.session.add.return_value = None
        db_mock.session.commit.side_effect = lambda: setattr(agent_schedule_mock, 'id', 1)  # id is set after commit
        db_mock.session.query.return_value.get.return_value = project_mock

        response = client.post("agents/schedule", json=mock_agent_config_schedule)

        assert response.status_code == 201
        assert response.json() == {
            "id": mock_agent.id,
            "name": mock_agent.name,
            "contentType": "Agents",
            "schedule_id": 1
        }


def test_create_and_schedule_agent_project_not_found(mock_agent_config_schedule):
    with patch('superagi.controllers.agent.db') as mock_db:
        # Set up the database query result
        mock_db.session.query.return_value.get.return_value = None

        # Call the endpoint
        response = client.post("agents/schedule", json=mock_agent_config_schedule)

        # Verify the HTTP response
        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found"}