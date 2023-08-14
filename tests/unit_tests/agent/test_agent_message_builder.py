import pytest
from unittest.mock import patch, Mock

from superagi.agent.agent_message_builder import AgentLlmMessageBuilder
from superagi.models.agent_execution_feed import AgentExecutionFeed


@patch('superagi.helper.token_counter.TokenCounter.token_limit')
@patch('superagi.config.config.get_config')
def test_build_agent_messages(mock_get_config, mock_token_limit):
    mock_session = Mock()
    llm = Mock()
    agent_id = 1
    agent_execution_id = 1
    prompt = "start"
    agent_feeds = []
    completion_prompt = "end"

    # Mocking
    mock_token_limit.return_value = 1000
    mock_get_config.return_value = 600

    builder = AgentLlmMessageBuilder(mock_session, llm, agent_id, agent_execution_id)
    messages = builder.build_agent_messages(prompt, agent_feeds, history_enabled=True, completion_prompt=completion_prompt)

    # Test prompt message
    assert messages[0] == {"role": "system", "content": prompt}

    # Test initial feeds
    assert mock_session.add.call_count == len(messages)
    assert mock_session.commit.call_count == len(messages)

    # Check if AgentExecutionFeed object is created and added to session
    for i in range(len(messages)):
        args, _ = mock_session.add.call_args_list[i]
        feed_obj = args[0]
        assert isinstance(feed_obj, AgentExecutionFeed)
        assert feed_obj.agent_execution_id == agent_execution_id
        assert feed_obj.agent_id == agent_id
        assert feed_obj.feed == messages[i]["content"]
        assert feed_obj.role == messages[i]["role"]

@patch('superagi.models.agent_execution_config.AgentExecutionConfiguration.fetch_value')
@patch('superagi.models.agent_execution_config.AgentExecutionConfiguration.add_or_update_agent_execution_config')
@patch('superagi.agent.agent_message_builder.AgentLlmMessageBuilder._build_prompt_for_recursive_ltm_summary_using_previous_ltm_summary')
@patch('superagi.agent.agent_message_builder.AgentLlmMessageBuilder._build_prompt_for_ltm_summary')
@patch('superagi.helper.token_counter.TokenCounter.count_text_tokens')
@patch('superagi.helper.token_counter.TokenCounter.token_limit')
def test_build_ltm_summary(mock_token_limit, mock_count_text_tokens, mock_build_prompt_for_ltm_summary,
                           mock_build_prompt_for_recursive_ltm_summary, mock_add_or_update_agent_execution_config,
                           mock_fetch_value):
    mock_session = Mock()
    llm = Mock()
    agent_id = 1
    agent_execution_id = 1

    builder = AgentLlmMessageBuilder(mock_session, llm, agent_id, agent_execution_id)

    past_messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
    output_token_limit = 100

    mock_token_limit.return_value = 1000
    mock_count_text_tokens.return_value = 200
    mock_build_prompt_for_ltm_summary.return_value = "ltm_summary_prompt"
    mock_build_prompt_for_recursive_ltm_summary.return_value = "recursive_ltm_summary_prompt"
    mock_fetch_value.return_value = Mock(value="ltm_summary")
    llm.chat_completion.return_value = {"content": "ltm_summary"}

    ltm_summary = builder._build_ltm_summary(past_messages, output_token_limit)

    assert ltm_summary == "ltm_summary"

    mock_add_or_update_agent_execution_config.assert_called_once()

    llm.chat_completion.assert_called_once_with([{"role": "system", "content": "You are GPT Prompt writer"},
                                                 {"role": "assistant", "content": "ltm_summary_prompt"}])

@patch('superagi.helper.prompt_reader.PromptReader.read_agent_prompt')
def test_build_prompt_for_ltm_summary(mock_read_agent_prompt):
    mock_session = Mock()
    llm = Mock()
    agent_id = 1
    agent_execution_id = 1

    builder = AgentLlmMessageBuilder(mock_session, llm, agent_id, agent_execution_id)

    past_messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
    token_limit = 100

    mock_read_agent_prompt.return_value = "{past_messages}\n{char_limit}"

    prompt = builder._build_prompt_for_ltm_summary(past_messages, token_limit)

    assert "user: Hello\nassistant: Hi\n" in prompt
    assert "400" in prompt


@patch('superagi.helper.prompt_reader.PromptReader.read_agent_prompt')
def test_build_prompt_for_recursive_ltm_summary_using_previous_ltm_summary(mock_read_agent_prompt):
    mock_session = Mock()
    llm = Mock()
    agent_id = 1
    agent_execution_id = 1

    builder = AgentLlmMessageBuilder(mock_session, llm, agent_id, agent_execution_id)

    previous_ltm_summary = "Summary"
    past_messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
    token_limit = 100

    mock_read_agent_prompt.return_value = "{previous_ltm_summary}\n{past_messages}\n{char_limit}"

    prompt = builder._build_prompt_for_recursive_ltm_summary_using_previous_ltm_summary(previous_ltm_summary, past_messages, token_limit)

    assert "Summary" in prompt
    assert "user: Hello\nassistant: Hi\n" in prompt
    assert "400" in prompt
