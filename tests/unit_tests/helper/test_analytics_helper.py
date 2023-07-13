import pytest
from sqlalchemy.exc import SQLAlchemyError
from superagi.models.events import Event
from superagi.apm.analytics_helper import AnalyticsHelper
from unittest.mock import MagicMock

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def analytics_helper(mock_session):
    return AnalyticsHelper(mock_session)

def test_create_event_success(analytics_helper, mock_session):
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    event = analytics_helper.create_event('test', 1, 1, 1, 100)

    assert isinstance(event, Event)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_create_event_failure(analytics_helper, mock_session):
    mock_session.commit = MagicMock(side_effect=SQLAlchemyError())
    event = analytics_helper.create_event('test', {}, 1, 1, 100)
    assert event is None

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

def test_calculate_tool_usage(analytics_helper, mock_session):
    mock_session.query().all.return_value = [MagicMock()]
    result = analytics_helper.calculate_tool_usage()
    assert isinstance(result, list)