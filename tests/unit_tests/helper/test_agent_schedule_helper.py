from unittest.mock import MagicMock, patch
import pytest
import datetime
from superagi.helper.agent_schedule_helper import AgentScheduleHelper

# Create pytest fixture for mocking session
@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_query():
    return MagicMock()

def test_create_execution_name_for_scheduling(mock_session, mock_query):
    # Arrange
    mock_agent_id = 1
    mock_user_timezone = MagicMock()
    mock_user_timezone.value = 'Asia/Kolkata'

    # Mocking the returned value from the first session query
    mock_query.filter().filter().first.return_value = mock_user_timezone

    with patch.object(mock_session, 'query', return_value=mock_query):

        # Act
        result = AgentScheduleHelper.create_execution_name_for_scheduling(mock_agent_id)

    # Assert
    assert isinstance(result, str)
    assert result.startswith("Run")


