from sqlalchemy import Column, Integer, String,Text
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.agent import Agent

class AgentExecution(DBBaseModel):
    __tablename__ = 'agent_executions'

    id = Column(Integer, primary_key=True)
    status = Column(String) #like ('CREATED', 'RUNNING', 'PAUSED', 'COMPLETED')
    logs = Column(Text)
    agent_id = Column(Integer)

    def __repr__(self):
        return f"AgentExecution(id={self.id}, status='{self.status}', " \
               f"logs='{self.logs}', agent_id={self.agent_id})"
