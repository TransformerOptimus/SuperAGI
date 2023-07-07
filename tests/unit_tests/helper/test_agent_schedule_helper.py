import pytest
from unittest.mock import patch, MagicMock, call
from superagi.helper.agent_schedule_helper import AgentScheduleHelper
from superagi.models.agent_schedule import AgentSchedule
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


@patch('superagi.helper.agent_schedule_helper.AgentScheduleHelper._AgentScheduleHelper__create_execution_name_for_scheduling')
@patch('superagi.helper.agent_schedule_helper.AgentScheduleHelper._AgentScheduleHelper__should_execute_agent')
@patch('superagi.helper.agent_schedule_helper.AgentScheduleHelper._AgentScheduleHelper__can_remove_agent')
@patch('superagi.helper.agent_schedule_helper.AgentScheduleHelper._AgentScheduleHelper__execute_schedule')
@patch('superagi.helper.agent_schedule_helper.parse_interval_to_seconds')
@patch('superagi.helper.agent_schedule_helper.AgentSchedule')
@patch('superagi.helper.agent_schedule_helper.Session')
@patch('superagi.helper.agent_schedule_helper.datetime')
def test_run_scheduled_agents(
    mock_datetime, 
    mock_session, 
    mock_agent_schedule, 
    mock_parse_interval_to_seconds, 
    mock_execute_schedule, 
    mock_can_remove_agent, 
    mock_should_execute_agent, 
    mock_create_execution_name_for_scheduling
):

    # Mocking current datetime
    mock_datetime.now.return_value = datetime(2022, 1, 1, 10, 0)

    # Mocking agent object
    mock_agent = MagicMock(spec=AgentSchedule)
    mock_agent.next_scheduled_time = datetime(2022, 1, 1, 9, 55)
    mock_agent.status = 'SCHEDULED'
    mock_agent.recurrence_interval = '5 Minutes'
    mock_agent.agent_id = 'agent_1'

    # Mocking the return value of the session query
    mock_session.return_value.query.return_value.filter.return_value.all.return_value = [mock_agent]
    mock_parse_interval_to_seconds.return_value = 300
    
    mock_should_execute_agent.return_value = True
    mock_can_remove_agent.return_value = False
    mock_create_execution_name_for_scheduling.return_value = 'Run 01 January 2022 10:00'

    # Call the method
    helper = AgentScheduleHelper()
    helper.run_scheduled_agents()

    # Assert that the mocks were called as expected
    mock_session.assert_called_once_with()
    mock_session.return_value.query.assert_called_once_with(mock_agent_schedule)
    mock_session.return_value.query.return_value.filter.assert_called_once()
    mock_session.return_value.query.return_value.filter.return_value.all.assert_called_once()
    
    mock_parse_interval_to_seconds.assert_has_calls([call('5 Minutes')])

    mock_should_execute_agent.assert_called_once_with(mock_agent, mock_agent.recurrence_interval)
    mock_can_remove_agent.assert_called_once_with(mock_agent, mock_agent.recurrence_interval)
    
    mock_execute_schedule.assert_has_calls([call(
        mock_should_execute_agent.return_value, 
        mock_parse_interval_to_seconds.return_value, 
        mock_session(), 
        mock_agent, 
        mock_create_execution_name_for_scheduling.return_value
    )])
    
    mock_create_execution_name_for_scheduling.assert_called_once_with(mock_agent.agent_id)
