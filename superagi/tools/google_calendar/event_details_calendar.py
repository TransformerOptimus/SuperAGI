import base64
from typing import Any, Type
from pydantic import BaseModel, Field
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.tools.base_tool import BaseTool
from superagi.helper.google_calendar_creds import GoogleCalendarCreds

class EventDetailsCalendarInput(BaseModel):
    event_id: str = Field(..., description="The id of event to be fetched from Google Calendar. if no value is given keep default value is None")

class EventDetailsCalendarTool(BaseTool):
    name: str = "Fetch Google Calendar Event"
    args_schema: Type[BaseModel] = EventDetailsCalendarInput
    description: str = "Fetch an event from Google Calendar"

    def _execute(self, event_id: str):
        service = GoogleCalendarCreds(self.toolkit_config.session).get_credentials(self.toolkit_config.toolkit_id)
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"
        if event_id == "None":
            return f"Add Event ID to fetch details of an event from Google Calendar"
        else:
            decoded_id = base64.b64decode(event_id)
            eid = decoded_id.decode("utf-8")
            eid  = eid.split(" ", 1)[0]
            result = service.events().get(
                calendarId = "primary",
                eventId = eid
            ).execute()
            if "summary" in result:
                summary = result['summary']
            if result['start'] and result['end']:
                start_date = result['start']['dateTime']
                end_date = result['end']['dateTime']
            attendees = []
            if "attendees" in result:
                for attendee in result['attendees']:
                    attendees.append(attendee['email'])
            attendees_str = ','.join(attendees)
            output_str = f"Event details for the event id '{event_id}' is - \nSummary : {summary}\nStart Date and Time : {start_date}\nEnd Date and Time : {end_date}\nAttendees : {attendees_str}"
            return output_str