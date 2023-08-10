from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.orm import Session

from superagi.models.base_model import DBBaseModel


class AgentExecutionFeed(DBBaseModel):
    """
    Feed of the agent execution.

    Attributes:
        id (int): The unique identifier of the agent execution feed.
        agent_execution_id (int): The identifier of the associated agent execution.
        agent_id (int): The identifier of the associated agent.
        feed (str): The feed content.
        role (str): The role of the feed entry. Possible values: 'system', 'user', or 'assistant'.
        extra_info (str): Additional information related to the feed entry.
    """

    __tablename__ = 'agent_execution_feeds'

    id = Column(Integer, primary_key=True)
    agent_execution_id = Column(Integer)
    agent_id = Column(Integer)
    feed = Column(Text)
    role = Column(String)
    extra_info = Column(String)

    def __repr__(self):
        """
        Returns a string representation of the AgentExecutionFeed object.

        Returns:
            str: String representation of the AgentExecutionFeed.
        """

        return f"AgentExecutionFeed(id={self.id}, " \
               f"agent_execution_id={self.agent_execution_id}, " \
               f"feed='{self.feed}', role='{self.role}', extra_info={self.extra_info})"

    @classmethod
    def get_last_tool_response(cls, session: Session, agent_execution_id: int, tool_name: str = None):
        agent_execution_feeds = session.query(AgentExecutionFeed).filter(
            AgentExecutionFeed.agent_execution_id == agent_execution_id,
            AgentExecutionFeed.role == "system").order_by(AgentExecutionFeed.created_at.desc()).all()

        for agent_execution_feed in agent_execution_feeds:
            if tool_name and not agent_execution_feed.feed.startswith(
                f"Tool {tool_name}"
            ):
                continue
            if agent_execution_feed.feed.startswith("Tool"):
                return agent_execution_feed.feed
        return ""
    
    @classmethod
    def get_tools_response(cls, session: Session, agent_execution_id: int, tool_names: list = None):
        """
        Returns all system generated responses by the tools
        Args:
            session : Current Agent Session running
            agent_execution_id (int) : Agent Execution id 
            tool name (list) : Tool Name(s), whose responses are to be queried
        Returns:
            list: List of responses queried
        """
        agent_execution_feeds = session.query(AgentExecutionFeed).filter(
            AgentExecutionFeed.agent_execution_id == agent_execution_id,
            AgentExecutionFeed.role == "system").all()

        return [
            agent_execution_feed.feed
            for agent_execution_feed in agent_execution_feeds
            if tool_names
            and any(
                agent_execution_feed.feed.startswith(f"Tool {x}")
                for x in tool_names
            )
        ]