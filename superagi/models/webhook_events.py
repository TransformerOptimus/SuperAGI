from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.agent_execution import AgentExecution


class WebhookEvents(DBBaseModel):
    """

    Attributes:
        

    Methods:
    """
    __tablename__ = 'webhook_events'

    id = Column(Integer, primary_key=True)
    agent_id=Column(Integer)
    run_id = Column(Integer)
    event = Column(String)
    status = Column(String)
    errors= Column(Text)
    

    
