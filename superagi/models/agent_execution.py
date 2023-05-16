from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base_model import BaseModel
from agent import Agent

class AgentExecution(BaseModel):
    __tablename__ = 'agent_executions'

    id = Column(Integer, primary_key=True)
    status = Column(Enum('CREATED', 'RUNNING', 'PAUSED', 'COMPLETED'))
    logs = Column(String)
    agent_id = Column(Integer, ForeignKey(Agent.id))
    agent = relationship(Agent)

    def __repr__(self):
        return f"AgentExecution(id={self.id}, status='{self.status}', " \
               f"logs='{self.logs}', agent_id={self.agent_id})"
