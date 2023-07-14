from sqlalchemy import Column, Integer, String, DateTime, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from superagi.models.base_model import DBBaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Event(DBBaseModel):
    """
    Represents an Event record in the database.

    Attributes:
        id (Integer): The unique identifier of the event.
        event_name (String): The name of the event.
        event_value (Integer): The value of the event.
        event_property (JSONB): The JSON object representing additional attributes of the event.
        agent_id (Integer): The ID of the agent.
        org_id (Integer): The ID of the organisation.
    """
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    event_name = Column(String, nullable=False)
    event_value = Column(Integer, nullable=False)
    event_property = Column(JSONB, nullable=True)
    agent_id = Column(Integer, nullable=True)
    org_id = Column(Integer, nullable=True)

    def __repr__(self):
        """
        Returns a string representation of the Event instance.
        """
        return f"Event(id={self.id}, event_name={self.event_name}, " \
               f"event_value={self.event_value}, " \
               f"agent_id={self.agent_id}, " \
               f"org_id={self.org_id})"