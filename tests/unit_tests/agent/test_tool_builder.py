import pytest
from unittest.mock import Mock, patch

from superagi.agent.tool_builder import ToolBuilder
from superagi.models.tool import Tool


@pytest.fixture
def session():
    return Mock()

@pytest.fixture
def agent_id():
    return 1

@pytest.fixture
def tool_builder(session, agent_id):
    return ToolBuilder(session, agent_id)

@pytest.fixture
def tool():
    tool = Mock(spec=Tool)
    tool.file_name = 'test.py'
    tool.folder_name = 'test_folder'
    tool.class_name = 'TestClass'
    return tool

@pytest.fixture
def agent_config():
    return {"model": "gpt4"}

@pytest.fixture
def agent_execution_config():
    return {"goal": "Test Goal", "instruction": "Test Instruction"}

@patch('superagi.agent.tool_builder.importlib.import_module')
@patch('superagi.agent.tool_builder.getattr')
def test_build_tool(mock_getattr, mock_import_module, tool_builder, tool):
    mock_module = Mock()
    mock_class = Mock()
    mock_import_module.return_value = mock_module
    mock_getattr.return_value = mock_class

    result_tool = tool_builder.build_tool(tool)

    mock_import_module.assert_called_with('.test_folder.test')
    mock_getattr.assert_called_with(mock_module, tool.class_name)

    assert result_tool.toolkit_config.session == tool_builder.session
    assert result_tool.toolkit_config.toolkit_id == tool.toolkit_id