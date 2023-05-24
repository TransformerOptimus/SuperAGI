from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
# from llm import LLM
# from tool import Tool
from sqlalchemy.dialects.postgresql import ARRAY

from superagi.models.agent import Agent
from superagi.models.base_model import DBBaseModel


class AgentConfiguration(DBBaseModel):
    __tablename__ = 'agent_configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey(Agent.id))
    agent = relationship(Agent)
    key = Column(String)
    value = Column(String)

    def __repr__(self):
        return f"AgentConfiguration(id={self.id}, key={self.key})"

    @classmethod
    def add_config(cls, session, agent_id, key, value):
        config = AgentConfiguration(agent_id=agent_id, key=key, value=value)
        session.add(config)
        session.commit()
        return config