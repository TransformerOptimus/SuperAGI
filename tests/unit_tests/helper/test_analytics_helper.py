from unittest.mock import MagicMock, patch, create_autospec, Mock
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, func
from superagi.models.events import Event
from superagi.helper.analytics_helper import AnalyticsHelper
from sqlalchemy.orm import Session

@pytest.fixture
def mock_session(monkeypatch):
    # Create an autospec mock for the Session
    # (A mock which simulates all methods and attributes of the actual class)
    mock_session = create_autospec(Session)
    monkeypatch.setattr('superagi.helper.analytics_helper.Session', lambda: mock_session)
    return mock_session

@pytest.fixture
def analytics_helper(mock_session):
    return AnalyticsHelper(mock_session)

    def test_analytics_helper_create_event_success(self, analytics_helper, mock_session):
        mock_session.commit = MagicMock()

        # Act
        event = analytics_helper.create_event('event1', 10, {'prop': 'value'}, 1, 1)

        # Assert
        assert isinstance(event, Event)
        mock_session.add.assert_called_once_with(event)
        mock_session.commit.assert_called_once()

    @patch('superagi.helper.analytics_helper.logging')
    def test_analytics_helper_create_event_failure(self, mock_logging, analytics_helper, mock_session):
        mock_session.commit = MagicMock(side_effect=SQLAlchemyError())

        # Act
        event = analytics_helper.create_event('event1', 10, {'prop': 'value'}, 1, 1)

        # Assert
        assert event is None
        assert mock_logging.error.called

    def test_calculate_run_completed_metrics(self, mock_session, analytics_helper):
        metrics = MagicMock()
        metrics.configure_mock(total_tokens=100, total_calls=20, runs_completed=10)
        mock_session.query().one.return_value = metrics
        assert analytics_helper.calculate_run_completed_metrics() == {'total_tokens': 100, 'total_calls': 20, 'runs_completed': 10}

    def test_fetch_agent_data(self, mock_session, analytics_helper):
        agent = MagicMock()
        agent.configure_mock(**{
            'agent_name': 'Agent1',
            'agent_id': 1,
            'runs_completed': 5,
            'total_calls': 10,
            'total_tokens': 50
        })
        model = MagicMock()
        model.configure_mock(**{
            'model': 'Model1',
            'agents': 1
        })

        mock_session.query().all.return_value = [[agent], [model]]

        assert analytics_helper.fetch_agent_data() == {
            'agent_details': [{
                'name': 'Agent1',
                'agent_id': 1,
                'runs_completed': 5,
                'total_calls': 10,
                'total_tokens': 50
            }],
            'model_info': [{
                'model': 'Model1',
                'agents': 1
            }]
        }

    def test_fetch_agent_runs(self, mock_session, analytics_helper):
        # Test data
        execution1 = {
            'agent_execution_name': 'Execution1',
            'tokens_consumed': 10,
            'calls': 5,
            'created_at': '2023-07-05T12:21:58.153551',
            'updated_at': '2023-07-05T12:22:58.153551'
        }
        execution2 = {
            'agent_execution_name': 'New Run',
            'tokens_consumed': 1989,
            'calls': 2,
            'created_at': '2023-07-05T12:21:58.153551',
            'updated_at': '2023-07-05T12:23:20.174844'
        }
        mock_session.query().all.return_value = [execution1, execution2]
        assert analytics_helper.fetch_agent_runs(1) == [{
            'name': 'Execution1',
            'tokens_consumed': 10,
            'calls': 5,
            'created_at': '2023-07-05T12:21:58.153551',
            'updated_at': '2023-07-05T12:22:58.153551'
        },
        {
            'name': 'New Run',
            'tokens_consumed': 1989,
            'calls': 2,
            'created_at': '2023-07-05T12:21:58.153551',
            'updated_at': '2023-07-05T12:23:20.174844'
        }]

    def test_calculate_tool_usage(self, mock_session, analytics_helper):
        # Test Data
        mock_row1 = Mock(tool_name='Finish', unique_agents=1, total_usage=1)
        mock_row2 = Mock(tool_name='Finish', unique_agents=1, total_usage=1)

        mock_query = mock_session.query.return_value
        mock_query.join.return_value.all.return_value = [mock_row1, mock_row2]

        result = analytics_helper.calculate_tool_usage()

        assert result == [{
            'tool_name': 'Finish',
            'unique_agents': 2,
            'total_usage': 2
        }]

        # Note: The exact calls to the SQLAlchemy Query API cannot easily be mocked and validated due to how SQLAlchemy internally works
        mock_session.query.assert_any_call()

        # Ensure that all() is called in the end to fetch the results
        assert mock_query.join.return_value.all.called