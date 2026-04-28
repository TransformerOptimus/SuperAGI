from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey,JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from superagi.models.base_model import DBBaseModel
from superagi.models.agent_execution import AgentExecution

class Webhooks(DBBaseModel):
    """

    Attributes:
        

    Methods:
    """
    __tablename__ = 'webhooks'

    id = Column(Integer, primary_key=True)
    name=Column(String)
    org_id = Column(Integer)
    url = Column(String)
    headers=Column(JSON)
    is_deleted=Column(Boolean)
    filters=Column(JSON)

    def __repr__(self):
        return f"Webhooks(id={self.id}, name={self.name}, org_id={self.org_id}, url={self.url})"

    __str__ = __repr__
