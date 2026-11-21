from unittest.mock import patch
from unittest import mock
import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.models.agent_schedule import AgentSchedule
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def mock_patch_schedule_input():
    return {
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

# An agent is already scheduled and is simply being updated, we assert for the updated values here
def test_schedule_existing_agent_already_scheduled(mock_patch_schedule_input, mock_schedule):
    with patch('superagi.controllers.agent_execution.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_schedule 

        response = client.post("agentexecutions/schedule", json=mock_patch_schedule_input)

        assert response.status_code == 201
        assert mock_schedule.start_time == datetime.strptime(mock_patch_schedule_input['start_time'], '%Y-%m-%d %H:%M:%S')
        assert mock_schedule.recurrence_interval == mock_patch_schedule_input['recurrence_interval']
        assert mock_schedule.expiry_date == datetime.strptime(mock_patch_schedule_input['expiry_date'], '%Y-%m-%d %H:%M:%S')
        assert mock_schedule.expiry_runs == mock_patch_schedule_input['expiry_runs']

# The agent isn't scheduled yet and we are scheduling it, we simply assert for a 201 status code and non-null schedule id.
def test_schedule_existing_agent_new_schedule(mock_patch_schedule_input, mock_schedule):
    with patch('superagi.controllers.agent_execution.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_schedule

        response = client.post("agentexecutions/schedule", json=mock_patch_schedule_input)

        assert response.status_code == 201
        assert response.json()["schedule_id"] is not None


@pytest.fixture
def mock_agent_run_input():
    return {
        "agent_id": 1,
        "name": "Test Run",
        "goal": ["Goal 1"],
        "instruction": ["Instruction 1"],
        "constraints": ["Constraint 1"],
        "toolkits": [],
        "exit": "No exit criterion",
        "tools": [],
        "iteration_interval": 500,
        "model": "gpt-4",
        "permission_type": "God Mode",
        "LTM_DB": None,
        "max_iterations": 10,
        "user_timezone": "UTC",
        "knowledge": None
    }


def test_create_agent_run_agent_not_found(mock_agent_run_input):
    with patch('superagi.controllers.agent_execution.db') as mock_db, \
         patch('superagi.controllers.agent_execution.get_user_organisation') as mock_get_org:
        mock_get_org.return_value = mock.Mock(id=1)
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        response = client.post("agentexecutions/add_run", json=mock_agent_run_input)

        assert response.status_code == 404
        assert response.json()["detail"] == "Agent not found"


def test_create_agent_run_cross_organisation_denied(mock_agent_run_input):
    with patch('superagi.controllers.agent_execution.db') as mock_db, \
         patch('superagi.controllers.agent_execution.get_user_organisation') as mock_get_org, \
         patch('superagi.controllers.agent_execution.Project') as mock_project:
        mock_get_org.return_value = mock.Mock(id=1)
        mock_agent = mock.Mock(id=1, is_deleted=False, project_id=10)
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_agent
        mock_project.find_by_id.return_value = mock.Mock(id=10, organisation_id=2)

        response = client.post("agentexecutions/add_run", json=mock_agent_run_input)

        assert response.status_code == 404
        assert response.json()["detail"] == "Agent not found"
