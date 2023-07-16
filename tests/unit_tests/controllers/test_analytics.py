from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app  # assuming your FastAPI app is defined here

client = TestClient(app)

@patch("superagi.helper.auth.get_user_organisation")
@patch("superagi.apm.analytics_helper.AnalyticsHelper.calculate_run_completed_metrics")
def test_get_metrics(mock_calculate_metrics, mock_get_org):
    mock_get_org.return_value.id = 1
    mock_calculate_metrics.return_value = {"metrics": "data"}
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {"metrics": "data"}

@patch("superagi.helper.auth.get_user_organisation")
@patch("superagi.apm.analytics_helper.AnalyticsHelper.fetch_agent_data")
def test_get_agents(mock_fetch_agent_data, mock_get_org):
    mock_get_org.return_value.id = 1
    mock_fetch_agent_data.return_value = {"agents": "data"}
    response = client.get("/agents/all")
    assert response.status_code == 200
    assert response.json() == {"agents": "data"}

@patch("superagi.helper.auth.get_user_organisation")
@patch("superagi.apm.analytics_helper.AnalyticsHelper.fetch_agent_runs")
def test_get_agent_runs(mock_fetch_agent_runs, mock_get_org):
    mock_get_org.return_value.id = 1
    mock_fetch_agent_runs.return_value = {"agent_runs": "data"}
    response = client.get("/agents/1")  # assuming an agent with id 1 exists
    assert response.status_code == 200
    assert response.json() == {"agent_runs": "data"}

@patch("superagi.helper.auth.get_user_organisation")
@patch("superagi.apm.analytics_helper.AnalyticsHelper.get_active_runs")
def test_get_active_runs(mock_get_active_runs, mock_get_org):
    mock_get_org.return_value.id = 1
    mock_get_active_runs.return_value = {"active_runs": "data"}
    response = client.get("/runs/active")
    assert response.status_code == 200
    assert response.json() == {"active_runs": "data"}

@patch("superagi.helper.auth.get_user_organisation")
@patch("superagi.apm.tools_handler.ToolsHandler.calculate_tool_usage")
def test_get_tools_used(mock_get_tools_used, mock_get_org):
    mock_get_org.return_value.id = 1
    mock_get_tools_used.return_value = {"tools_used": "data"}
    response = client.get("/tools/used")
    assert response.status_code == 200
    assert response.json() == {"tools_used": "data"}