import pytest
from unittest.mock import MagicMock, call
from sqlalchemy.orm.exc import NoResultFound
from superagi.models.tool import Tool
from superagi.controllers.types.agent_with_config import AgentConfigInput
from fastapi import HTTPException
from typing import List

@pytest.fixture
def mock_session():
    session = MagicMock()
    get_mock = MagicMock()
    get_mock.side_effect = [MagicMock(), NoResultFound()]   # assuming 2nd tool won't be found
    session.query.return_value.get = get_mock
    return session


def test_get_invalid_tools(mock_session):
    # Set up the mock session such that the second tool is not found
    mock_session.query.return_value.get.side_effect = [MagicMock(), None]

    # Call the get_invalid_tools method with tool_ids as [1, 2]
    invalid_tool_ids = Tool.get_invalid_tools([1, 2], mock_session)

    # Assert that the returned invalid tool IDs is as expected
    assert invalid_tool_ids == [2]

    # Assert that mock_session.query().get() was called with the correct arguments
    calls = [call(Tool).get(1), call(Tool).get(2)]
    mock_session.query.assert_has_calls(calls, any_order=True)



