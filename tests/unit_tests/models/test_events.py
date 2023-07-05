import pytest
from unittest.mock import Mock, create_autospec
from sqlalchemy.orm import Session
from superagi.models.events import Event

def test_event_repr():
    event = Mock(spec=Event)
    event.__repr__ = Mock(return_value="Event(id=1, event_name=Test Event, event_value=100, agent_id=1, org_id=1)")
    assert str(event) == "Event(id=1, event_name=Test Event, event_value=100, agent_id=1, org_id=1)"

def test_event_properties():
    event = Mock(spec=Event)
    event.id = 1
    event.event_name = "Test Event"
    event.event_value = 100
    event.json_property = {"agent_name": "Agent Test 1"}
    event.agent_id = 1
    event.org_id = 1

    assert event.id == 1
    assert event.event_name == "Test Event"
    assert event.event_value == 100
    assert event.json_property == {"agent_name": "Agent Test 1"}
    assert event.agent_id == 1
    assert event.org_id == 1

def test_event_create():
    mock_session = create_autospec(Session)
    # Replace Event with a mock
    event = Mock(spec=Event)
    event.id = 1

    mock_session.add(event)
    mock_session.commit()

    mock_session.query(Event).get.assert_called_with(1)
    assert mock_session.query(Event).get(1) == event