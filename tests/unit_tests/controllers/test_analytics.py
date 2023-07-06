from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.models.events import Event

client = TestClient(app)


@pytest.fixture
def mock_event_data():
    return [
        Event(
            id=1,
            event_name="event1",
            event_value=100,
            json_property={},
            agent_id=1,
            org_id=1
        ),
        Event(
            id=2,
            event_name="event2",
            event_value=200,
            json_property={},
            agent_id=2,
            org_id=2
        ),
        Event(
            id=3,
            event_name="event3",
            event_value=300,
            json_property={},
            agent_id=3,
            org_id=3
        )
    ]


@pytest.mark.parametrize("endpoint,status_code", [
    ("/metrics", 200),
    ("/agents/all", 200),
    ("/agents/1", 200),
    ("/runs/active", 200),
    ("/tools/used", 200)
])
def test_analytics_endpoints(endpoint, status_code, mock_event_data):
    with patch('superagi.helper.analytics_helper.AnalyticsHelper') as mock_helper:
        mock_helper.return_value.calculate_run_completed_metrics.return_value = {
            'total_tokens': 0,
            'total_calls': 0,
            'runs_completed': 3
        }
        mock_helper.return_value.fetch_agent_data.return_value = {'agent_details': [], 'model_info': []}
        mock_helper.return_value.fetch_agent_runs.return_value = []
        mock_helper.return_value.get_active_runs.return_value = []
        mock_helper.return_value.calculate_tool_usage.return_value = []

        response = client.get(endpoint, headers={"Authorization": "Bearer test_token"})

        assert response.status_code == status_code