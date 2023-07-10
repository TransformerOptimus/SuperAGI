import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from superagi.models.configuration import Configuration
from superagi.models.agent import Agent
from superagi.models.organisation import Organisation
from superagi.models.project import Project


def test_fetch_configuration():
    mock_session = MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_query.filter_by.return_value.first.return_value = Configuration(value="test_value")

    result = Configuration.fetch_configuration(mock_session, 1, "test_key")

    assert result == "test_value"
    mock_session.query.assert_called_once_with(Configuration)
    mock_query.filter_by.assert_called_once_with(organisation_id=1, key="test_key")


def test_fetch_value_by_agent_id():
    mock_session = MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_query.filter.return_value.first.side_effect = [
        Agent(project_id=1), Project(organisation_id=1), Organisation(id=1), Configuration(value="test_value")
    ]

    result = Configuration.fetch_value_by_agent_id(mock_session, 1, "test_key")

    assert result == "test_value"
    assert mock_session.query.call_count == 4


def test_fetch_value_by_agent_id_agent_not_found():
    mock_session = MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_query.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exception_info:
        Configuration.fetch_value_by_agent_id(mock_session, 1, "test_key")

    assert exception_info.value.status_code == 404
    assert exception_info.value.detail == "Agent not found"
