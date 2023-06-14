import os 
import csv
from datetime import datetime, timezone, timedelta
from typing import Type
from superagi.config.config import get_config
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool

from superagi.helper.google_calendar_creds import GoogleCalendarCreds

class ListCalendarEventsInput(BaseModel):
    number_of_results: int = Field(..., description="The number of events to get from the calendar, default value is 0.")
    start_date: str = Field(..., description="The start date to return events from the calendar in format 'yyyy-mm-dd' in a string variable, default value is 'None'.")
    end_date: str = Field(..., description="The end date to return events from the calendar in format 'yyyy-mm-dd' in a string variable, default value is 'None'.")

class ListCalendarEventsTool(BaseTool):
    name: str = "List Calendar Events"
    args_schema: Type[BaseModel] = ListCalendarEventsInput
    description: str = "Get the list of all the events from Google Calendar"

    def _execute(self, number_of_results: int, start_date: str, end_date: str):
        service = GoogleCalendarCreds().get_credentials()
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"
        
        if start_date == 'None':
            print("////////////////////////////////")
            start_date = datetime.now()
            start_datetime_utc = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            print(start_datetime_utc)
        else:
            print("/////////////////////////////////")
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            start_datetime_utc = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            print(start_datetime_utc)

        if number_of_results != 0:
            event_results = (
                service.events().list(
                calendarId = "primary",
                timeMin = start_datetime_utc,
                maxResults=number_of_results,
                singleEvents = True,
                orderBy = "startTime",
                timeZone = 'UTC',
                ).execute()
            )
            print(number_of_results)
        else:
            if end_date == 'None':
                end_datetime_utc = start_date + timedelta(days=1) - timedelta(microseconds=1)
            else:
                print("/////////////////////////////////")
                end_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_datetime_utc = start_date.replace(hour=0, minute=59, second=59, microsecond=999999)
                print(end_datetime_utc)
            
            event_results = (
                service.events().list(
                calendarId = "primary",
                timeMin = start_datetime_utc,
                timeMax = end_datetime_utc,
                singleEvents = True,
                orderBy = "startTime",
                timeZone = 'UTC',
                ).execute()
            )
        allDayEvents = [["Event Title", "Date"], *[[e.get("summary"), e.get("start").get("date")] for e in event_results.get("items", []) if e.get("start").get("date") and e.get("end").get("date")]]
        file_name = "Google_Calendar_" + start_datetime_utc + ".csv"
        final_path = file_name
        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + file_name
        else:
            final_path = os.getcwd() + "/" + file_name
        
        with open(final_path, "w") as file:
            writer = csv.writer(file, lineterminator="\n")
            writer.writerows(allDayEvents)
        
        return f"List of Google Calendar Events successfully stored in {file_name}."
