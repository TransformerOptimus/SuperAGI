from sqlalchemy import Column, Integer, Text,String
from superagi.models.base_model import DBBaseModel
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from superagi.models.agent import Agent
from sqlalchemy.dialects.postgresql import ARRAY


class AgentConfiguration(DBBaseModel):
    __tablename__ = 'agent_configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        return f"AgentConfiguration(id={self.id}, key={self.key}, value={self.value})"
