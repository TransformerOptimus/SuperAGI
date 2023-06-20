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
        toolkit_id = self.tool_kit_config.tool_kit_id
        service = GoogleCalendarCreds().get_credentials(toolkit_id)
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"
        
        date_utc = CalendarDate().get_date_utc(start_date,end_date,start_time,end_time,service)

        event_results = (
            service.events().list(
            calendarId = "primary",
            timeMin = date_utc['start_datetime_utc'],
            timeMax = date_utc['end_datetime_utc'],
            singleEvents = True,
            orderBy = "startTime",
            ).execute()
        )
        
        if not event_results:
            return f"No events found for the given date and time range."
        
        csv_data = [['Event ID','Event Name','Start Time','End Time','Attendees']]
        for item in event_results['items']:
            eid_url = item["htmlLink"]
            parsed_url = urlparse(eid_url)
            query_parameters = parse_qs(parsed_url.query)
            event_id = query_parameters.get('eid',[None])[0]
            summary = ""
            start_date = ""
            end_date = ""
            if "summary" in item:
                summary = item['summary']
            if item['start'] and item['end']:
                start_date = item['start']['dateTime']
                end_date = item['end']['dateTime']
            attendees = []
            if "attendees" in item:
                for attendee in item['attendees']:
                    attendees.append(attendee['email'])
            attendees_str = ','.join(attendees)
            csv_data.append([event_id,summary,start_date,end_date,attendees_str])
        
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
        with open(final_path, 'rb') as file:
            resource = ResourceHelper.make_written_file_resource(file_name=file_name,
                                                                     agent_id=self.agent_id, file=file,
                                                                     channel="OUTPUT")
            if resource is not None:
                self.session.add(resource)
                self.session.commit()
                self.session.flush()
                if resource.storage_type == "S3":
                    s3_helper = S3Helper()
                    s3_helper.upload_file(file, path=resource.path)
                    logger.info("Resource Uploaded to S3!")
            self.session.close()
        
        return f"List of Google Calendar Events month successfully stored in {file_name}."
