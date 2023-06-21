import os
import csv
from datetime import datetime
from typing import Type
from superagi.config.config import get_config
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.helper.google_calendar_creds import GoogleCalendarCreds
from superagi.helper.calendar_date import CalendarDate
from superagi.helper.resource_helper import ResourceHelper
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

    def _execute(self, start_time: str = 'None', start_date: str = 'None', end_date: str = 'None', end_time: str = 'None'):
        service = self.get_google_calendar_service()
        if not service["success"]:
            return f"Kindly connect to Google Calendar"
        
        date_utc = CalendarDate().get_date_utc(start_date, end_date, start_time, end_time, service["service"])
        event_results = self.get_event_results(service["service"], date_utc)
        if not event_results:
            return f"No events found for the given date and time range."
        
        csv_data = self.generate_csv_data(event_results)
        file_name = self.create_output_file(csv_data)
        resource = self.create_resource(file_name)
        if resource is not None:
            self.upload_resource_to_s3_and_commit(resource)
        return f"List of Google Calendar Events month successfully stored in {file_name}."

    def get_google_calendar_service(self):
        engine = connect_db()
        Session = sessionmaker(bind=engine)
        session = Session()
        toolkit_id = self.tool_kit_config.tool_kit_id
        return GoogleCalendarCreds().get_credentials(toolkit_id)

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

    def create_output_file(self, csv_data):
        file = datetime.now()
        file = file.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        file_name = "Google_Calendar_" + file + ".csv"
        final_path = self.get_output_path(file_name)
        with open(final_path, "w") as file:
            writer = csv.writer(file, lineterminator="\n")
            for row in csv_data:
                writer.writerow(row)
        return file_name

    def get_output_path(self, file_name):
        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + file_name
        else:
            final_path = os.getcwd() + "/" + file_name
        return final_path

    def create_resource(self, file_name):
        with open(self.get_output_path(file_name), 'rb') as file:
            resource = ResourceHelper.make_written_file_resource(file_name=file_name,
                                                                 agent_id=self.agent_id, file=file,
                                                                 channel="OUTPUT")
        return resource

    def upload_resource_to_s3_and_commit(self, resource):
        engine = connect_db()
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(resource)
        session.commit()
        session.flush()
        if resource.storage_type == "S3":
            s3_helper = S3Helper()
            with open(self.get_output_path(resource.file_name), 'rb') as file:
                s3_helper.upload_file(file, path=resource.path)
            logger.info("Resource Uploaded to S3!")
        session.close()