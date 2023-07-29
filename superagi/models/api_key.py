from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.agent_execution import AgentExecution


class ApiKey(DBBaseModel):
    """

    Attributes:
        

    Methods:
    """
    __tablename__ = 'api_key'

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer)
    key_name = Column(String)
    key = Column(String)
    

    
