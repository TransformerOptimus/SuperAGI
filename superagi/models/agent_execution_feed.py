from sqlalchemy import Column, Integer, Text, String

from superagi.models.base_model import DBBaseModel


class AgentExecutionFeed(DBBaseModel):
    """
    Represents a feed entry for an agent execution.

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
