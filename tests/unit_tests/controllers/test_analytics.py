from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch('superagi.controllers.analytics.db')
def test_get_metrics_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
                patch('superagi.controllers.analytics.db') as mock_db, \
                patch('superagi.controllers.analytics.AnalyticsHelper') as mock_helper, \
                patch('superagi.helper.auth.db') as mock_auth_db:
        mock_helper().calculate_run_completed_metrics.return_value = {'total_tokens': 10, 'total_calls': 5, 'runs_completed': 2}
        response = client.get("/analytics/metrics")
        assert response.status_code == 200
        assert response.json() == {'total_tokens': 10, 'total_calls': 5, 'runs_completed': 2}

@patch('superagi.controllers.analytics.db')
def test_get_agents_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
                    patch('superagi.controllers.analytics.db') as mock_db, \
                    patch('superagi.controllers.analytics.AnalyticsHelper') as mock_helper, \
                    patch('superagi.helper.auth.db') as mock_auth_db:
        mock_helper().fetch_agent_data.return_value = {"agent_details": "mock_details", "model_info": "mock_info"}
        response = client.get("/analytics/agents/all")
        assert response.status_code == 200
        assert response.json() == {"agent_details": "mock_details", "model_info": "mock_info"}

@patch('superagi.controllers.analytics.db')
def test_get_agent_runs_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
                    patch('superagi.controllers.analytics.db') as mock_db, \
                    patch('superagi.controllers.analytics.AnalyticsHelper') as mock_helper, \
                    patch('superagi.helper.auth.db') as mock_auth_db:
        mock_helper().fetch_agent_runs.return_value = "mock_agent_runs"
        response = client.get("/analytics/agents/1")
        assert response.status_code == 200
        assert response.json() == "mock_agent_runs"

@patch('superagi.controllers.analytics.db')
def test_get_active_runs_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
                    patch('superagi.controllers.analytics.db') as mock_db, \
                    patch('superagi.controllers.analytics.AnalyticsHelper') as mock_helper, \
                    patch('superagi.helper.auth.db') as mock_auth_db:
        mock_helper().get_active_runs.return_value = ["mock_run_1", "mock_run_2"]
        response = client.get("/analytics/runs/active")
        assert response.status_code == 200
        assert response.json() == ["mock_run_1", "mock_run_2"]

@patch('superagi.controllers.analytics.db')
def test_get_tools_user_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
                    patch('superagi.controllers.analytics.db') as mock_db, \
                    patch('superagi.controllers.analytics.ToolsHandler') as mock_handler, \
                    patch('superagi.helper.auth.db') as mock_auth_db:
        mock_handler().calculate_tool_usage.return_value = ["tool1", "tool2"]
        response = client.get("/analytics/tools/used")
        assert response.status_code == 200
        assert response.json() == ["tool1", "tool2"]