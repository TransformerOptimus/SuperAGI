import pytest
from unittest.mock import Mock, create_autospec
from sqlalchemy.orm import Session
from superagi.models.agent_execution_feed import AgentExecutionFeed


def test_get_last_tool_response():
    mock_session = create_autospec(Session)
    agent_execution_feed_1 = AgentExecutionFeed(id=1, agent_execution_id=2, feed="Tool test1", role='system')
    agent_execution_feed_2 = AgentExecutionFeed(id=2, agent_execution_id=2, feed="Tool test2", role='system')

    mock_session.query().filter().order_by().all.return_value = [agent_execution_feed_1, agent_execution_feed_2]

    result = AgentExecutionFeed.get_last_tool_response(mock_session, 2)

    assert result == agent_execution_feed_1.feed  # as agent_execution_feed_1 should be the latest based on created_at


def test_get_last_tool_response_with_tool_name():
    mock_session = create_autospec(Session)
    agent_execution_feed_1 = AgentExecutionFeed(id=1, agent_execution_id=2, feed="Tool test1", role='system')
    agent_execution_feed_2 = AgentExecutionFeed(id=2, agent_execution_id=2, feed="Tool test2", role='system')

    mock_session.query().filter().order_by().all.return_value = [agent_execution_feed_1, agent_execution_feed_2]

    result = AgentExecutionFeed.get_last_tool_response(mock_session, 2, "test2")
    assert result == agent_execution_feed_2.feed
