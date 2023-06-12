from sqlalchemy import Column, Integer, Text, String, Boolean
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.agent_execution import AgentExecution


class AgentExecutionPermission(DBBaseModel):
    __tablename__ = 'agent_execution_permissions'

    id = Column(Integer, primary_key=True)
    agent_execution_id = Column(Integer)
    agent_id = Column(Integer)
    status = Column(Boolean)
    response = Column(Text)

    def __repr__(self):
        return f"AgentExecutionPermission(id={self.id}, " \
               f"agent_execution_id={self.agent_execution_id}, " \
               f"agent_id={self.agent_id}, " \
               f"status={self.status}, " \
               f"response={self.response})"
