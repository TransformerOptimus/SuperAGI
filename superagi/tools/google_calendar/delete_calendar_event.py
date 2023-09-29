import base64
from typing import Any, Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.helper.google_calendar_creds import GoogleCalendarCreds

class DeleteCalendarEventInput(BaseModel):
    event_id: str = Field(..., description="The id of event to be deleted from Google Calendar. default value is None")

class DeleteCalendarEventTool(BaseTool):
    name: str = "Delete Google Calendar Event"
    args_schema: Type[BaseModel] = DeleteCalendarEventInput
    description: str = "Delete an event from Google Calendar"



    def _execute(self, event_id: str):
        service = GoogleCalendarCreds(self.toolkit_config.session).get_credentials(self.toolkit_config.toolkit_id)
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"
        if event_id == "None":
            return f"Add Event ID to delete an event from Google Calendar"
        else:
            if len(event_id) % 4 != 0:  
                event_id += "=" * (4 - (len(event_id) % 4))  
            decoded_id = base64.b64decode(event_id)
            eid = decoded_id.decode("utf-8")
            eid  = eid.split(" ", 1)[0]
            result = service.events().delete(
                calendarId = "primary",
                eventId = eid
            ).execute()
            return f"Event Successfully deleted from your Google Calendar"
