import os 
import csv
import datetime
from typing import Type
from superagi.config.config import get_config
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from googleapiclient.discovery import build
from superagi.helper.go

class ListCalendarEventsInput(BaseModel):
    number_of_results: int = Field(..., description="The number of events to get from the calendar, default value is 0.")
    start_date: str = Field(..., description="The start date to return events from the calendar in format 'yyyy-mm-dd' in a string variable, default value is 'None'.")
    end_date: str = Field(..., description="The end date to return events from the calendar in format 'yyyy-mm-dd' in a string variable, default value is 'None'.")

class ListCalendarEventsTool(BaseTool):
    name: str = "List Calendar Events"
    args_schema: Type[BaseModel] = ListCalendarEventsInput
    description: str = "Get the list of all the events from Google Calendar"

    def _execute(self, number_of_results: int, start_date: str, end_date: str):
        print("/////////////////////////////////////")
        print(number_of_results)
        print(start_date)
        print(end_date)
        service = GoogleCalendarCreds().get_credentials()
        print("////////////////////////////////////////////////")
        print(service)
#         if not service:
#             return f"Kindly Connect to Google Calendar"
        if start_date == 'None':
            start_date = datetime.date.today()
        elif isinstance(start_date, str):
            start_date = datetime.date.fromisoformat(start_date)

        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

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
                end_date = datetime.date.today()
            elif isinstance(start_date, str):
                end_date = datetime.date.fromisoformat(end_date)
            
            end_datetime = datetime.datetime.combine(end_date, datetime.time.min)
            end_datetime_utc = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
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
        file_name = "Google_Calendar_" + start_datetime + ".csv"
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
