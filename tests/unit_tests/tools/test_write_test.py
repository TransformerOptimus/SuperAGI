import pytest
from unittest.mock import Mock, patch
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.manager import ResourceManager
from superagi.lib.logger import logger
from superagi.tools.code.write_test import WriteTestTool
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager


def test_write_test_tool_init():
    tool = WriteTestTool()
    assert tool.llm is None
    assert tool.agent_id is None
    assert tool.name == "WriteTestTool"
    assert tool.description is not None
    assert tool.goals == []
    assert tool.resource_manager is None


@patch('superagi.tools.code.write_test.logger')
@patch('superagi.tools.code.write_test.TokenCounter')
def test_write_test_tool_execute(mock_token_counter, mock_logger):
    # Given
    mock_llm = Mock(spec=BaseLlm)
    mock_llm.get_model.return_value = None
    mock_llm.chat_completion.return_value = {"content": "```python\nsample_code\n```"}
    mock_token_counter.count_message_tokens.return_value = 0
    mock_token_counter.token_limit.return_value = 100

    mock_resource_manager = Mock(spec=ResourceManager)
    mock_resource_manager.write_file.return_value = "No error"

    mock_tool_response_manager = Mock(spec=ToolResponseQueryManager)
    mock_tool_response_manager.get_last_response.return_value = ""

    tool = WriteTestTool()
    tool.llm = mock_llm
    tool.resource_manager = mock_resource_manager
    tool.tool_response_manager = mock_tool_response_manager

    # When
    result = tool._execute("spec", "test_file")

    # Then
    mock_llm.chat_completion.assert_called_once()
    mock_resource_manager.write_file.assert_called_once_with("test_file", "python\nsample_code")
    assert "Tests generated and saved successfully in test_file" in result
