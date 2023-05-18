from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base_model import DBBaseModel
from agent_execution import AgentExecution

class AgentExecutionFeed(DBBaseModel):
    __tablename__ = 'agent_execution_feeds'

    id = Column(Integer, primary_key=True)
    agent_execution_id = Column(Integer, ForeignKey(AgentExecution.id))
    feed = Column(String)
    type = Column(Enum('HUMAN', 'SYSTEM', 'AI'))
    agent_execution = relationship(AgentExecution)

    def __repr__(self):
        return f"AgentExecutionFeed(id={self.id}, " \
               f"agent_execution_id={self.agent_execution_id}, " \
               f"feed='{self.feed}', type='{self.type}')"
