from types import SimpleNamespace
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.helper.auth import get_user_organisation
from superagi.models.agent import Agent
from superagi.models.agent_schedule import AgentSchedule
from datetime import datetime

client = TestClient(app)


@pytest.fixture(autouse=True)
def current_organisation():
    organisation = SimpleNamespace(id=1)
    app.dependency_overrides[get_user_organisation] = lambda: organisation
    yield organisation
    app.dependency_overrides.pop(get_user_organisation, None)

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
    agent = Agent(id=1, project_id=1, is_deleted=False)
    agent.get_agent_organisation = lambda session: SimpleNamespace(id=1)
    with patch('superagi.controllers.agent_execution.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.first.side_effect = [agent, mock_schedule]

        response = client.post("agentexecutions/schedule", json=mock_patch_schedule_input)

        assert response.status_code == 201
        assert mock_schedule.start_time == datetime.strptime(mock_patch_schedule_input['start_time'], '%Y-%m-%d %H:%M:%S')
        assert mock_schedule.recurrence_interval == mock_patch_schedule_input['recurrence_interval']
        assert mock_schedule.expiry_date == datetime.strptime(mock_patch_schedule_input['expiry_date'], '%Y-%m-%d %H:%M:%S')
        assert mock_schedule.expiry_runs == mock_patch_schedule_input['expiry_runs']

# The agent isn't scheduled yet and we are scheduling it, we simply assert for a 201 status code and non-null schedule id.
def test_schedule_existing_agent_new_schedule(mock_patch_schedule_input, mock_schedule):
    agent = Agent(id=1, project_id=1, is_deleted=False)
    agent.get_agent_organisation = lambda session: SimpleNamespace(id=1)
    with patch('superagi.controllers.agent_execution.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.first.side_effect = [agent, mock_schedule]

        response = client.post("agentexecutions/schedule", json=mock_patch_schedule_input)

        assert response.status_code == 201
        assert response.json()["schedule_id"] is not None


def test_schedule_existing_agent_rejects_cross_organisation(mock_patch_schedule_input):
    agent = Agent(id=1, project_id=1, is_deleted=False)
    agent.get_agent_organisation = lambda session: SimpleNamespace(id=2)
    with patch('superagi.controllers.agent_execution.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.first.return_value = agent

        response = client.post("agentexecutions/schedule", json=mock_patch_schedule_input)

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}
        mock_db.session.add.assert_not_called()


def test_schedule_existing_agent_returns_not_found_for_missing_agent(mock_patch_schedule_input):
    with patch('superagi.controllers.agent_execution.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        response = client.post("agentexecutions/schedule", json=mock_patch_schedule_input)

        assert response.status_code == 404
        assert response.json() == {"detail": "Agent not found"}
        mock_db.session.add.assert_not_called()
