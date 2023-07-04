import pytest
from unittest.mock import patch, MagicMock
from superagi.helper.agent_schedule_helper import AgentScheduleHelper
from datetime import datetime, timedelta

@patch('superagi.helper.agent_schedule_helper.parse_interval_to_seconds')
@patch('superagi.models.agent_schedule.AgentSchedule')
@patch('superagi.helper.agent_schedule_helper.Session')
@patch('superagi.helper.agent_schedule_helper.datetime')
def test_update_next_scheduled_time(mock_datetime, mock_session, mock_agent_schedule, mock_parse_interval_to_seconds):
    
    mock_datetime.now.return_value = datetime(2022, 1, 1, 10, 0)

    # Mock agent object
    mock_agent = MagicMock()
    mock_agent.start_time = datetime(2022, 1, 1, 1, 0)
    mock_agent.next_scheduled_time = datetime(2022, 1, 1, 1, 0)
    mock_agent.recurrence_interval = '5 Minutes'
    mock_agent.status = 'SCHEDULED'

    mock_agent_schedule.return_value = mock_agent

    # Mock the return value of the session query
    mock_session.return_value.query.return_value.filter.return_value.all.return_value = [mock_agent]
    mock_parse_interval_to_seconds.return_value = 300

    # Call the method
    helperObj = AgentScheduleHelper()
    helperObj.update_next_scheduled_time()

    # Assert that the mocks were called as expected
    mock_session.assert_called_once()
    mock_session.return_value.query.assert_called_once()
    mock_session.return_value.query.return_value.filter.assert_called()
    mock_session.return_value.query.return_value.filter.return_value.all.assert_called_once()
    mock_parse_interval_to_seconds.assert_called_once_with('5 Minutes')
    assert mock_agent.status == 'SCHEDULED'
