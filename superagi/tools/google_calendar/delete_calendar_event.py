import os 
from typing import Any, Type
from superagi.config.config import get_config
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.helper.google_calendar_creds import GoogleCalendarCreds


class DeleteCalendarEventInput(BaseModel):
    event_id: str = Field(..., description="The id of event to be deleted from Google Calendar. default value is None")

class DeleteCalendarEventTools(BaseTool):
    name: str = "Delete Calendar Event"
    args_schema: Type[BaseModel] = DeleteCalendarEventInput
    description: str = "Delete an event from Google Calendar"

    def _execute(self, event_id: str):
        service = GoogleCalendarCreds().get_credentials()
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"
        
        if event_id == "None":
            return f"Add Event ID to delete an event from Google Calendar"
        else:
            result = service.events().delete(
                calendarId = "primary",
                eventId = event_id
            ).execute()
            print("///////////////////////////")
            print(result)
            return f"Event Successfully deleted from your Google Calendar"