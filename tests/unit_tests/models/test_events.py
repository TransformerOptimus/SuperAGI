from unittest.mock import MagicMock, patch

import pytest

from superagi.models.events import Event

@pytest.fixture
def mock_session():
    return MagicMock()

def test_create_event(mock_session):
    # Arrange
    event_name = "example_event"
    event_value = 100
    agent_id = 1
    org_id = 1
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    event = Event(event_name=event_name, event_value=event_value)
    mock_session.add(event)

    # Assert
    mock_session.add.assert_called_once_with(event)

def test_repr_method_event(mock_session):
    # Arrange
    event_name = "example_event"
    event_value = 100
    agent_id = 1
    org_id = 1
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    event = Event(event_name=event_name, event_value=event_value)
    event_repr = repr(event)

    # Assert
    assert event_repr == f"Event(id=None, event_name={event_name}, " \
                         f"event_value={event_value}, " \
                         f"agent_id=None, " \
                         f"org_id=None)"
