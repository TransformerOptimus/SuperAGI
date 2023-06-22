import pytest
from unittest.mock import Mock, patch
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.manager import ResourceManager
from superagi.lib.logger import logger
from superagi.tools.code.write_test import WriteTestTool


def test_write_test_tool_init():
    tool = WriteTestTool()
    assert tool.llm is None
    assert tool.agent_id is None
    assert tool.name == "WriteTestTool"
    assert tool.description is not None
    assert tool.goals == []
    assert tool.resource_manager is None


@patch.object(logger, 'error')
@patch.object(ResourceManager, 'write_file')
def test_write_test_tool_execute(mock_write_file, mock_logger):
    # Given
    mock_llm = Mock(spec=BaseLlm)
    llm_response = {"content": "```python\nsample_code\n```"}
    mock_llm.chat_completion.return_value = llm_response
    mock_write_file.return_value = "Tests generated and saved successfully in test_file"

    tool = WriteTestTool()
    tool.llm = mock_llm
    tool.resource_manager = ResourceManager(session=None)

    # When
    result = tool._execute("spec", "test_file")

    # Then
    mock_llm.chat_completion.assert_called_once()
    mock_write_file.assert_called_once_with("test_file", "sample_code")
    assert ("Tests generated and saved successfully in test_file" in result) == True


def test_write_test_tool_execute_with_exception():
    # Given
    mock_llm = Mock(spec=BaseLlm)
    mock_llm.chat_completion.side_effect = Exception("Mock error")

    tool = WriteTestTool()
    tool.llm = mock_llm
    tool.resource_manager = Mock()

    # When
    tool._execute("spec", "test_file")

    # Then
    mock_llm.chat_completion.assert_called_once()
