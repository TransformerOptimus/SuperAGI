from typing import Any, Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.helper.google_calendar_creds import GoogleCalendarCreds
from superagi.helper.calendar_date import CalendarDate

class CreateEventCalendarInput(BaseModel):
    event_name: str = Field(..., description="Name of the event/meeting to be scheduled, if not given craete a name depending on description.")
    description: str = Field(..., description="Description of the event/meeting to be scheduled.")
    start_date: str = Field(..., description="Start date of the event to be scheduled in format 'yyyy-mm-dd', if no value is given keep the default value as 'None'.")
    start_time: str = Field(..., description="Start time of the event to be scheduled in format 'hh:mm:ss', if no value is given keep the default value as 'None'.")
    end_date: str = Field(..., description="End Date of the event to be scheduled in format 'yyyy-mm-dd', if no value is given keep the default value as 'None'.")
    end_time: str = Field(..., description="End Time of the event to be scheduled in format 'hh:mm:ss', if no value is given keep the default value as 'None'.")
    attendees: list = Field(..., description="List of attendees email ids to be invited for the event.")
    location: str = Field(..., description="Geographical location of the event. if no value is given keep the default value as 'None'")

class CreateEventCalendarTool(BaseTool):
    name: str = "Create Google Calendar Event"
    args_schema: Type[BaseModel] = CreateEventCalendarInput
    description: str = "Create an event for Google Calendar"

    def _execute(self, event_name: str, description: str, attendees: list, start_date: str = 'None', start_time: str = 'None', end_date: str = 'None', end_time: str = 'None', location: str = 'None'):
        session = self.toolkit_config.session
        toolkit_id = self.toolkit_config.toolkit_id
        service = GoogleCalendarCreds(session).get_credentials(toolkit_id)
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"
        date_utc = CalendarDate().create_event_dates(service, start_date, start_time, end_date, end_time)
        attendees_list = []
        for attendee in attendees:
            email_id = {
                "email": attendee
            }
            attendees_list.append(email_id)
        event = {
            "summary": event_name,
            "description": description,
            "start": {
                "dateTime": date_utc["start_datetime_utc"],
                "timeZone": date_utc["timeZone"]
            },
            "end": {
                "dateTime": date_utc["end_datetime_utc"],
                "timeZone": date_utc["timeZone"]
            },
            "attendees": attendees_list
        }
        if location != "None":
            event["location"] = location
        else:
            event["conferenceData"] = {
                "createRequest": {
                    "requestId": f"meetSample123",
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    },
                },
            }
        event = service.events().insert(calendarId="primary", body=event, conferenceDataVersion=1).execute()
        output_str = f"Event {event_name} at {date_utc['start_datetime_utc']} created successfully, link for the event {event.get('htmlLink')}"
        return output_str
