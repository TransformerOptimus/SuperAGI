from unittest.mock import patch, Mock
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch('fastapi_jwt_auth.AuthJWT')
@patch('superagi.helper.auth.get_user_organisation')
@patch('superagi.apm.analytics_helper.AnalyticsHelper.calculate_run_completed_metrics')
def test_get_metrics_success(mock_metrics_class, mock_auth_function, mock_jwt_function):
    mock_metrics_class.return_value = {'total_tokens': 10,'total_calls': 5, 'runs_completed': 2}
    mock_jwt_function.return_value.verify_jwt_in_request.return_value = None
    response = client.get("analytics/metrics")
    assert response.status_code == 200
    assert response.json() == {'total_tokens': 10, 'total_calls': 5, 'runs_completed': 2}

@patch('fastapi_jwt_auth.AuthJWT')
@patch('superagi.helper.auth.get_user_organisation')
@patch('superagi.apm.analytics_helper.AnalyticsHelper.fetch_agent_data')
def test_get_agents_success(mock_agent_class, mock_auth_function, mock_jwt_function):
    mock_agent_class.return_value = {"agent_details": "mock_details", "model_info": "mock_info"}
    mock_jwt_function.return_value.verify_jwt_in_request.return_value = None
    response = client.get("analytics/agents/all")
    assert response.status_code == 200
    assert response.json() == {"agent_details": "mock_details", "model_info": "mock_info"}

@patch('fastapi_jwt_auth.AuthJWT')
@patch('superagi.helper.auth.get_user_organisation')
@patch('superagi.apm.analytics_helper.AnalyticsHelper.fetch_agent_runs')
def test_get_agent_runs_success(mock_agent_class, mock_auth_function, mock_jwt_function):
    mock_agent_class.return_value = "mock_agent_runs"
    mock_jwt_function.return_value.verify_jwt_in_request.return_value = None
    response = client.get("analytics/agents/1")
    assert response.status_code == 200
    assert response.json() == "mock_agent_runs"

@patch('fastapi_jwt_auth.AuthJWT')
@patch('superagi.helper.auth.get_user_organisation')
@patch('superagi.apm.analytics_helper.AnalyticsHelper.get_active_runs')
def test_get_active_runs_success(mock_run_class, mock_auth_function, mock_jwt_function):
    mock_run_class.return_value = ["mock_run_1", "mock_run_2"]
    mock_jwt_function.return_value.verify_jwt_in_request.return_value = None
    response = client.get("analytics/runs/active")
    assert response.status_code == 200
    assert response.json() == ["mock_run_1", "mock_run_2"]

@patch('fastapi_jwt_auth.AuthJWT')
@patch('superagi.helper.auth.get_user_organisation')
@patch('superagi.apm.tools_handler.ToolsHandler.calculate_tool_usage')
def test_get_tools_user_success(mock_tools_class, mock_auth_function, mock_jwt_function):
    mock_tools_class.return_value = ["tool1", "tool2"]
    mock_jwt_function.return_value.verify_jwt_in_request.return_value = None
    response = client.get("analytics/tools/used")
    assert response.status_code == 200
    assert response.json() == ["tool1", "tool2"]