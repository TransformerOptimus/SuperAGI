from unittest.mock import Mock, patch

from superagi.tools.code.write_test import WriteTestTool


def test_write_test_tool_init():
    tool = WriteTestTool()
    assert tool.llm is None
    assert tool.agent_id is None
    assert tool.name == "WriteTestTool"
    assert tool.description is not None
    assert tool.goals == []
    assert tool.resource_manager is None

@patch('superagi.tools.code.write_test.PromptReader')
@patch('superagi.tools.code.write_test.AgentPromptBuilder')
@patch('superagi.tools.code.write_test.TokenCounter')
def test_execute(mock_token_counter, mock_agent_prompt_builder, mock_prompt_reader):
    test_tool = WriteTestTool()
    test_tool.tool_response_manager = Mock()
    test_tool.resource_manager = Mock()
    test_tool.llm = Mock()

    test_tool.tool_response_manager.get_last_response.return_value = 'WriteSpecTool response'
    mock_prompt_reader.read_tools_prompt.return_value = 'Prompt template {goals} {test_description} {spec}'
    mock_agent_prompt_builder.add_list_items_to_string.return_value = 'Goals string'
    test_tool.llm.get_model.return_value = 'Model'
    mock_token_counter.count_message_tokens.return_value = 100
    mock_token_counter.token_limit.return_value = 1000
    test_tool.llm.chat_completion.return_value = {
        'content': 'File1\n```\nCode1```File2\n```\nCode2```',
    }
    test_tool.resource_manager.write_file.return_value = 'Success'

    result = test_tool._execute('Test description', 'test_file.py')

    assert 'File1' in result
    assert 'Code1' in result
    assert 'File2' in result
    assert 'Code2' in result
    assert 'Tests generated and saved successfully in test_file.py' in result

    mock_prompt_reader.read_tools_prompt.assert_called_once()
    mock_agent_prompt_builder.add_list_items_to_string.assert_called_once_with(test_tool.goals)
    test_tool.tool_response_manager.get_last_response.assert_called()
    test_tool.llm.get_model.assert_called()
    mock_token_counter.count_message_tokens.assert_called()
    mock_token_counter.token_limit.assert_called()
    test_tool.llm.chat_completion.assert_called()
    assert test_tool.resource_manager.write_file.call_count == 2