import os 
import csv
from datetime import datetime, timedelta
from typing import Type
from superagi.config.config import get_config
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
import googleapiclient.discovery as discovery
from superagi.helper.google_calendar_creds import GoogleCalendarCreds

class ListCalendarEventsInput(BaseModel):
    number_of_results: int = Field(..., description="The number of events to get from the calendar, default value is 0.")
    start_date: str = Field(..., description="The start date to return events from the calendar in format 'yyyy-mm-dd' in a string variable, default value is 'None'.")
    end_date: str = Field(..., description="The end date to return events from the calendar in format 'yyyy-mm-dd' in a string variable, default value is 'None'.")

class ListCalendarEventsTool(BaseTool):
    name: str = "List Google Calendar Events"
    args_schema: Type[BaseModel] = ListCalendarEventsInput
    description: str = "Get the list of all the events from Google Calendar"

    def _execute(self, number_of_results: int, start_date: str, end_date: str):
        service = GoogleCalendarCreds().get_credentials()
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"
        
        if start_date == 'None':
            start_date = datetime.now()
            start_datetime_utc = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            start_datetime_utc = start_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            print(start_datetime_utc)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            start_datetime_utc = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            start_datetime_utc = start_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if number_of_results != 0:
            event_results = (
                service.events().list(
                calendarId = "primary",
                timeMin = start_datetime_utc,
                maxResults=number_of_results,
                singleEvents = True,
                orderBy = "startTime",
                ).execute()
            )
        else:
            if end_date == 'None':
                end_datetime_utc = start_date + timedelta(days=1) - timedelta(microseconds=1)
                end_datetime_utc = end_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                end_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_datetime_utc = start_date.replace(hour=0, minute=59, second=59, microsecond=999999)
                end_datetime_utc = end_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            event_results = (
                service.events().list(
                calendarId = "primary",
                timeMin = start_datetime_utc,
                timeMax = end_datetime_utc,
                singleEvents = True,
                orderBy = "startTime",
                ).execute()
            )
        print("---------------------------------------")
        csv_data = [['Summary','Start Time','End Time','Attendees']]
        for item in event_results['items']:
            summary = item['summary']
            if item['start'] and item['end']:
                start_date = item['start']['dateTime']
                end_date = item['end']['dateTime']
            attendees = []
            for attendee in item['attendees']:
                attendees.append(attendee['email'])
            attendees_str = ','.join(attendees)
            csv_data.append([summary,start_date,end_date,attendees_str])

        file = datetime.now()
        file = file.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        file_name = "Google_Calendar_" + file + ".csv"
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
            for row in csv_data:
                writer.writerow(row)
        
        return f"List of Google Calendar Events successfully stored in {file_name}."
