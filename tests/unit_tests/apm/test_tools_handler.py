import pytest
from unittest.mock import MagicMock

from superagi.apm.tools_handler import ToolsHandler
from sqlalchemy.orm import Session

@pytest.fixture
def organisation_id():
    return 1

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def tools_handler(mock_session, organisation_id):
    return ToolsHandler(mock_session, organisation_id)

def test_calculate_tool_usage(tools_handler, mock_session):
    mock_session.query().all.return_value = [MagicMock()]
    result = tools_handler.calculate_tool_usage()
    assert isinstance(result, list)