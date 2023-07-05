import pytest
from unittest.mock import create_autospec
from sqlalchemy.orm import Session
from superagi.models.events import Event

def test_event_repr():
    event = Event(id=1, event_name="Test Event", event_value=100, agent_id=1, org_id=1)

    assert str(event) == "Event(id=1, event_name=Test Event, event_value=100, agent_id=1, org_id=1)"

def test_event_properties():
    event = Event(id=1, event_name="Test Event", event_value=100, agent_id=1, org_id=1)

    assert event.id == 1
    assert event.event_name == "Test Event"
    assert event.event_value == 100
    assert event.agent_id == 1
    assert event.org_id == 1

def test_event_json_property():
    event = Event(id=1, event_name="Test Event", event_value=100, json_property={"agent_name": "Agent Test 1"}, agent_id=1, org_id=1)

    assert event.json_property == {"agent_name": "Agent Test 1"}

def test_event_create():
    mock_session = create_autospec(Session)
    event = Event(id=1, event_name="Test Event", event_value=100, agent_id=1, org_id=1)

    mock_session.add(event)
    mock_session.commit()

    mock_session.query(Event).get.assert_called_with(1)
    assert mock_session.query(Event).get(1) == event