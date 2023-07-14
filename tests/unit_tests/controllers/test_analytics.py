from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# add a fixture for organisation
@pytest.fixture
def mock_organisation():
    mock_org = MagicMock()
    mock_org.id = 1
    return mock_org

# updated the test functions to use mock_organisation
@patch('superagi.helper.auth.get_user_organisation', return_value=mock_organisation)
def test_get_metrics_success(get_user_organisation):
    with patch('superagi.controllers.analytics.AnalyticsHelper') as mock_helper:
        mock_helper().calculate_run_completed_metrics.return_value = {'total_tokens': 10, 'total_calls': 5, 'runs_completed': 2}
        response = client.get("analytics/metrics")
        assert response.status_code == 200
        assert response.json() == {'total_tokens': 10, 'total_calls': 5, 'runs_completed': 2}

@patch('superagi.helper.auth.get_user_organisation', return_value=mock_organisation)
def test_get_agents_success(get_user_organisation):
    with patch('superagi.controllers.analytics.AnalyticsHelper') as mock_helper:
        mock_helper().fetch_agent_data.return_value = {"agent_details": "mock_details", "model_info": "mock_info"}
        response = client.get("analytics/agents/all")
        assert response.status_code == 200
        assert response.json() == {"agent_details": "mock_details", "model_info": "mock_info"}

@patch('superagi.helper.auth.get_user_organisation', return_value=mock_organisation)
def test_get_agent_runs_success(get_user_organisation):
    with patch('superagi.controllers.analytics.AnalyticsHelper') as mock_helper:
        mock_helper().fetch_agent_runs.return_value = "mock_agent_runs"
        response = client.get("analytics/agents/1")
        assert response.status_code == 200
        assert response.json() == "mock_agent_runs"

@patch('superagi.helper.auth.get_user_organisation', return_value=mock_organisation)
def test_get_active_runs_success(get_user_organisation):
    with patch('superagi.controllers.analytics.AnalyticsHelper') as mock_helper:
        mock_helper().get_active_runs.return_value = ["mock_run_1", "mock_run_2"]
        response = client.get("analytics/runs/active")
        assert response.status_code == 200
        assert response.json() == ["mock_run_1", "mock_run_2"]

@patch('superagi.helper.auth.get_user_organisation', return_value=mock_organisation)
def test_get_tools_user_success(get_user_organisation):
    with patch('superagi.controllers.analytics.ToolsHandler') as mock_handler:
        mock_handler().calculate_tool_usage.return_value = ["tool1", "tool2"]
        response = client.get("analytics/tools/used")
        assert response.status_code == 200
        assert response.json() == ["tool1", "tool2"]