import os
import csv
from datetime import datetime
from typing import Type
from superagi.config.config import get_config
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.helper.google_calendar_creds import GoogleCalendarCreds
from superagi.helper.calendar_date import CalendarDate
from superagi.resource_manager.file_manager import FileManager
from superagi.helper.s3_helper import S3Helper
from urllib.parse import urlparse, parse_qs
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.lib.logger import logger


class ListCalendarEventsInput(BaseModel):
    start_time: str = Field(..., description="A string variable storing the start time to return events from the calendar in format 'HH:MM:SS'. if no value is given keep default value as 'None'")
    start_date: str = Field(..., description="A string variable storing the start date to return events from the calendar in format 'yyyy-mm-dd' in a string variable, if no value is given keep default value as 'None'.")
    end_date: str = Field(..., description="A string variable storing the end date to return events from the calendar in format 'yyyy-mm-dd' in a string variable, if no value is given keep default value as 'None'.")
    end_time: str = Field(..., description="A string variable storing the end time to return events from the calendar in format 'HH:MM:SS'. if no value is given keep default value as 'None'")


class ListCalendarEventsTool(BaseTool):
    name: str = "List Google Calendar Events"
    args_schema: Type[BaseModel] = ListCalendarEventsInput
    description: str = "Get the list of all the events from Google Calendar"
    agent_id: int  = None
    resource_manager: FileManager = None

    def _execute(self, start_time: str = 'None', start_date: str = 'None', end_date: str = 'None', end_time: str = 'None'):
        service = self.get_google_calendar_service()
        if not service["success"]:
            return f"Kindly connect to Google Calendar"
        
        date_utc = CalendarDate().get_date_utc(start_date, end_date, start_time, end_time, service["service"])
        event_results = self.get_event_results(service["service"], date_utc)
        if not event_results:
            return f"No events found for the given date and time range."
        
        csv_data = self.generate_csv_data(event_results)
        file_name = self.create_output_file()
        if file_name is not None:
            self.resource_manager.write_csv_file(file_name, csv_data)
        return f"List of Google Calendar Events month successfully stored in {file_name}."

    def get_google_calendar_service(self):
        return GoogleCalendarCreds(self.toolkit_config.session).get_credentials(self.toolkit_config.toolkit_id)

    def get_event_results(self, service, date_utc):
        return (
            service.events().list(
            calendarId="primary",
            timeMin=date_utc['start_datetime_utc'],
            timeMax=date_utc['end_datetime_utc'],
            singleEvents=True,
            orderBy="startTime",
            ).execute()
        )

    def generate_csv_data(self, event_results):
        csv_data = [['Event ID', 'Event Name', 'Start Time', 'End Time', 'Attendees']]
        for item in event_results['items']:
            event_id, summary, start_date, end_date, attendees_str = self.parse_event_data(item)
            csv_data.append([event_id, summary, start_date, end_date, attendees_str])
        return csv_data

    def parse_event_data(self, item):
        eid_url = item["htmlLink"]
        parsed_url = urlparse(eid_url)
        query_parameters = parse_qs(parsed_url.query)
        event_id = query_parameters.get('eid', [None])[0]
        summary = item.get('summary', '')
        start_date = item['start'].get('dateTime', '')
        end_date = item['end'].get('dateTime', '')
        attendees = [attendee['email'] for attendee in item.get('attendees', [])]
        attendees_str = ','.join(attendees)
        return event_id, summary, start_date, end_date, attendees_str

    def create_output_file(self):
        file = datetime.now()
        file = file.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        file_name = "Google_Calendar_" + file + ".csv"
        return file_name
