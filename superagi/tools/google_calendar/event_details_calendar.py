from typing import Any, Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.helper.google_calendar_creds import GoogleCalendarCreds


class EventDetailsCalendarInput(BaseModel):
    event_id: str = Field(..., description="The id of event to be fetched from Google Calendar. if no value is given keep default value is None")

class EventDetailsCalendarTools(BaseTool):
    name: str = "Fetch Google Calendar Event"
    args_schema: Type[BaseModel] = EventDetailsCalendarInput
    description: str = "Fetch an event from Google Calendar"

    def _execute(self, event_id: str):
        service = GoogleCalendarCreds().get_credentials()
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"
        
        if event_id == "None":
            return f"Add Event ID to fetch details of an event from Google Calendar"
        else:
            result = service.events().delete(
                calendarId = "primary",
                eventId = event_id
            ).execute()
            print(result)
            return f"Event Successfully deleted from your Google Calendar"