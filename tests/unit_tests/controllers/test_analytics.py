import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from superagi.helper.analytics_helper import AnalyticsHelper

client = TestClient(app)

def test_get_metrics_success():
    # Mock the AnalyticsHelper
    with patch('superagi.helper.analytics_helper.AnalyticsHelper') as mock_analytics_helper:
        # Set up test data
        test_data = {
            "total_tokens": 200,
            "total_calls": 14,
            "run_completed": 2
        }

        # Mock the return value
        mock_analytics_helper().calculate_run_completed_metrics.return_value = test_data

        # Call the function
        response = client.get("/metrics")

        # Assertions
        assert response.status_code == 200
        assert response.json() == test_data

def test_get_agents_success():
   with patch('superagi.helper.analytics_helper.AnalyticsHelper') as mock_analytics_helper:
        # Set up test data
        test_data = [{"id": 1,"name": "Agent X","type": "type1"},{"id": 2,"name": "Agent Y","type": "type2"}]

        # Mock the return value
        mock_analytics_helper().fetch_agent_data.return_value = test_data

        # Call the function
        response = client.get("/agents/all")

        # Assertions
        assert response.status_code == 200
        assert response.json() == test_data

def test_get_agent_runs_success():
    with patch('superagi.helper.analytics_helper.AnalyticsHelper') as mock_analytics_helper:
        # Set up test data
        agent_id = 1
        test_data = [{"agent_execution_id": 101,"status": "completed","date": "2022-01-01"},
        {"agent_execution_id": 102,"status": "in progress","date": "2022-01-02"}]

        # Mock the return value
        mock_analytics_helper().fetch_agent_runs.return_value = test_data

        # Call the function
        response = client.get(f"/agents/{agent_id}")

        # Assertions
        assert response.status_code == 200
        assert response.json() == test_data


def test_get_active_runs_success():
    with patch('superagi.helper.analytics_helper.AnalyticsHelper') as mock_analytics_helper:
        # Set up test data
        test_data = [{"agent_execution_id": 101,"agent_id": 1},{"agent_execution_id": 102,"agent_id": 2}]

        # Mock the return value
        mock_analytics_helper().get_active_runs.return_value = test_data

        # Call the function
        response = client.get("/runs/active")

        # Assertions
        assert response.status_code == 200
        assert response.json() == test_data


def test_get_tools_used_success():
    with patch('superagi.helper.analytics_helper.AnalyticsHelper') as mock_analytics_helper:
        # Set up test data
        test_data = {"tool_x": 10,"tool_y": 5,"tool_z": 15}

        # Mock the return value
        mock_analytics_helper().calculate_tool_usage.return_value = test_data

        # Call the function
        response = client.get("/tools/used")

        # Assertions
        assert response.status_code == 200
        assert response.json() == test_data