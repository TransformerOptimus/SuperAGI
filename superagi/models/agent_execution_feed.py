from sqlalchemy import Column, Integer, Text, String, ForeignKey
from sqlalchemy.orm import relationship

from superagi.models.agent import Agent
from superagi.models.base_model import DBBaseModel
from superagi.models.agent_execution import AgentExecution

class AgentExecutionFeed(DBBaseModel):
    __tablename__ = 'agent_execution_feeds'

    id = Column(Integer, primary_key=True)
    agent_execution_id = Column(Integer, ForeignKey(AgentExecution.id))
    agent_id = Column(Integer, ForeignKey(Agent.id))
    feed = Column(Text)
    role = Column(String)
    agent_execution = relationship(AgentExecution)
    agent = relationship(Agent)

    def __repr__(self):
        return f"AgentExecutionFeed(id={self.id}, " \
               f"agent_execution_id={self.agent_execution_id}, " \
               f"feed='{self.feed}', type='{self.type}')"
