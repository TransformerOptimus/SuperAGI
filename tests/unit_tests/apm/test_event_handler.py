import pytest
from sqlalchemy.exc import SQLAlchemyError
from superagi.models.events import Event
from unittest.mock import MagicMock

from superagi.apm.event_handler import EventHandler

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def event_handler(mock_session):
    return EventHandler(mock_session)

def test_create_event_success(event_handler, mock_session):
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    event = event_handler.create_event('test', {}, 1, 1, 100)

    assert isinstance(event, Event)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_create_event_failure(event_handler, mock_session):
    mock_session.commit = MagicMock(side_effect=SQLAlchemyError())
    event = event_handler.create_event('test', {}, 1, 1, 100)
    assert event is None