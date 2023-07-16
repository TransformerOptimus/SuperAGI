import pytest
from unittest.mock import MagicMock
from superagi.apm.analytics_helper import AnalyticsHelper
from sqlalchemy.orm import Session

@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

@pytest.fixture
def organisation_id():
    return 1

@pytest.fixture
def analytics_helper(mock_session, organisation_id):
    return AnalyticsHelper(mock_session, organisation_id)

def test_calculate_run_completed_metrics(analytics_helper, mock_session):
    analytics_helper.calculate_run_completed_metrics = MagicMock(return_value = {})
    result = analytics_helper.calculate_run_completed_metrics()
    assert isinstance(result, dict)
    analytics_helper.calculate_run_completed_metrics.assert_called()

def test_fetch_agent_data(analytics_helper, mock_session):
    analytics_helper.fetch_agent_data = MagicMock(return_value = {})
    result = analytics_helper.fetch_agent_data()
    assert isinstance(result, dict)
    analytics_helper.fetch_agent_data.assert_called()

def test_fetch_agent_runs(analytics_helper, mock_session):
    agent_id = 1
    analytics_helper.fetch_agent_runs = MagicMock(return_value = [])
    result = analytics_helper.fetch_agent_runs(agent_id)
    assert isinstance(result, list)
    analytics_helper.fetch_agent_runs.assert_called_with(agent_id)

def test_get_active_runs(analytics_helper, mock_session):
    analytics_helper.get_active_runs = MagicMock(return_value = [])
    result = analytics_helper.get_active_runs()
    assert isinstance(result, list)
    analytics_helper.get_active_runs.assert_called()