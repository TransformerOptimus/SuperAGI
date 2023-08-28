from sqlalchemy import Column, Integer, String, Text

from superagi.models.base_model import DBBaseModel


class WebhookEvents(DBBaseModel):
    """

    Attributes:


    Methods:
    """

    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer)
    run_id = Column(Integer)
    event = Column(String)
    status = Column(String)
    errors = Column(Text)
