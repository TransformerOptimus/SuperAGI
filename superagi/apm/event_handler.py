import logging
from typing import Optional, Dict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from superagi.models.events import Event

class EventHandler:

    def __init__(self, session: Session):
        self.session = session

    def create_event(self, event_name: str, event_property: Dict, agent_id: int,
                     org_id: int, event_value: int = 1) -> Optional[Event]:
        try:
            event = Event(
                event_name=event_name,
                event_value=event_value,
                event_property=event_property,
                agent_id=agent_id,
                org_id=org_id,
            )
            self.session.add(event)
            self.session.commit()
            return event
        except SQLAlchemyError as err:
            logging.error(f"Error while creating event: {str(err)}")
            return None