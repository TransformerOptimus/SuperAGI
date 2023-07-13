import pytest
from unittest.mock import MagicMock

from superagi.apm.tools_handler import ToolsHandler

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def tools_handler(mock_session):
    return ToolsHandler(mock_session)

def test_calculate_tool_usage(tools_handler, mock_session):
    mock_session.query().all.return_value = [MagicMock()]
    result = tools_handler.calculate_tool_usage()
    assert isinstance(result, list)