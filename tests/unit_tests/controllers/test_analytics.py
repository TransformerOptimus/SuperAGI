from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from superagi.apm.analytics import router as analytics_router
from superagi.models.organisation import Organisation
from superagi.apm.analytics_helper import AnalyticsHelper
from fastapi import FastAPI

app = FastAPI()
app.include_router(analytics_router)

client = TestClient(app)

organisation = Organisation(id=1)
metrics = {"total_tokens": 1000, "total_calls": 500, "runs_completed": 80}
agents = [{"id": 1, "name": "agent1"}, {"id": 2, "name": "agent2"}]
runs = [{"id": 1, "run_name": "run1"}, {"id": 2, "run_name": "run2"}]
active_runs = [{"id": 1, "run_name": "run1", "status": "active"}, {"id": 2, "run_name": "run2", "status": "active"}]
tools_used = [{"tool_id": 1, "tool_name": "tool1"}, {"tool_id": 2, "tool_name": "tool2"}]

class MockAnalyticsHelper:
    def __init__(self, session, organisation_id):
        pass

    def calculate_run_completed_metrics(self):
        return metrics

    def fetch_agent_data(self):
        return agents

    def fetch_agent_runs(self, agent_id):
        return runs

    def get_active_runs(self):
        return active_runs


class MockToolsHandler:
    def __init__(self, session, organisation_id):
        pass

    def calculate_tool_usage(self):
        return tools_used


@pytest.fixture
def mock_get_user_organisation():
    return organisation

@patch("superagi.apm.analytics.AnalyticsHelper", new=MockAnalyticsHelper)
@patch("superagi.apm.analytics.ToolsHandler", new=MockToolsHandler)
@patch("superagi.apm.analytics.get_user_organisation", mock_get_user_organisation)
def test_route_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == metrics

@patch("superagi.apm.analytics.AnalyticsHelper", new=MockAnalyticsHelper)
@patch("superagi.apm.analytics.get_user_organisation", mock_get_user_organisation)
def test_route_agents():
    response = client.get("/agents/all")
    assert response.status_code == 200
    assert response.json() == agents

@patch("superagi.apm.analytics.AnalyticsHelper", new=MockAnalyticsHelper)
@patch("superagi.apm.analytics.get_user_organisation", mock_get_user_organisation)
def test_route_agents_runs():
    response = client.get("/agents/1")
    assert response.status_code == 200
    assert response.json() == runs

@patch("superagi.apm.analytics.AnalyticsHelper", new=MockAnalyticsHelper)
@patch("superagi.apm.analytics.get_user_organisation", mock_get_user_organisation)
def test_route_active_runs():
    response = client.get("/runs/active")
    assert response.status_code == 200
    assert response.json() == active_runs

@patch("superagi.apm.analytics.ToolsHandler", new=MockToolsHandler)
@patch("superagi.apm.analytics.get_user_organisation", mock_get_user_organisation)
def test_route_tools_used():
    response = client.get("/tools/used")
    assert response.status_code == 200
    assert response.json() == tools_used