import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from superagi.apm.tools_handler import ToolsHandler

@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

@pytest.fixture
def organisation_id():
    return 1

@pytest.fixture
def tools_handler(mock_session, organisation_id):
    return ToolsHandler(mock_session, organisation_id)

def test_calculate_tool_usage(tools_handler):
    tools_handler.calculate_tool_usage = MagicMock(return_value=[])
    result = tools_handler.calculate_tool_usage()
    assert isinstance(result, list)
    tools_handler.calculate_tool_usage.assert_called()