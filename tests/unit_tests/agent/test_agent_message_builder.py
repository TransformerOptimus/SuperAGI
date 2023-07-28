import pytest
from unittest.mock import patch, Mock

from superagi.agent.agent_message_builder import AgentLlmMessageBuilder
from superagi.models.agent_execution_feed import AgentExecutionFeed

@patch('superagi.helper.token_counter.TokenCounter.token_limit')
@patch('superagi.config.config.get_config')
def test_build_agent_messages(mock_get_config, mock_token_limit):
    mock_session = Mock()
    llm_model = 'model_1'
    agent_id = 1
    agent_execution_id = 1
    prompt = "start"
    agent_feeds = []
    completion_prompt = "end"

    # Mocking
    mock_token_limit.return_value = 1000
    mock_get_config.return_value = 600

    builder = AgentLlmMessageBuilder(mock_session, llm_model, agent_id, agent_execution_id)
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
