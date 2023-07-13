import pytest
from superagi.models.events import Event
from superagi.apm.analytics_helper import AnalyticsHelper
from unittest.mock import MagicMock

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def analytics_helper(mock_session):
    return AnalyticsHelper(mock_session)

def test_calculate_run_completed_metrics(analytics_helper, mock_session):
    mock_session.query().all.return_value = [MagicMock()]
    result = analytics_helper.calculate_run_completed_metrics()
    assert isinstance(result, dict)

def test_fetch_agent_data(analytics_helper, mock_session):
    mock_session.query().all.return_value = [MagicMock()]
    result = analytics_helper.fetch_agent_data()
    assert isinstance(result, dict)

def test_fetch_agent_runs(analytics_helper, mock_session):
    mock_session.query().all.return_value = [MagicMock()]
    result = analytics_helper.fetch_agent_runs(1)
    assert isinstance(result, list)

def test_get_active_runs(analytics_helper, mock_session):
    mock_session.query().all.return_value = [MagicMock()]
    result = analytics_helper.get_active_runs()
    assert isinstance(result, list)