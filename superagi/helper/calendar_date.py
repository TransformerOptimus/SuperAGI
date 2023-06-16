from datetime import datetime, timedelta, timezone
import pytz
from dateutil import tz

class CalendarDate():
    def get_date_utc(self,start_date,end_date,start_time,end_time,service):
        local_tz = self.get_time_zone(service)
        local_tz = pytz.timezone(local_tz)
        gmt_tz = pytz.timezone("GMT")
        if start_date == 'None':
            start_date = datetime.now(timezone.utc)
            start_datetime = start_date.replace(day=1,hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = str(start_date)
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if start_time == 'None':
                start_datetime = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start_time = str(start_time)
                time_obj = datetime.strptime(start_time, "%H:%M:%S")
                start_datetime = start_date.replace(hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second)
            
            local_start_date = local_tz.localize(start_datetime)
            start_datetime = local_start_date.astimezone(gmt_tz)
        if end_date == 'None':
            end_datetime = start_date + timedelta(days=30) - timedelta(microseconds=1)
        else:
            end_date = str(end_date)
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            if end_time == 'None':
                end_datetime = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                end_time = str(end_time)
                time_obj = datetime.strptime(end_time, "%H:%M:%S")
                end_datetime = end_date.replace(hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second)

            local_end_date = local_tz.localize(end_datetime)
            end_datetime = local_end_date.astimezone(gmt_tz)
       
        start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_datetime_utc = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        date_utc = {
            "start_datetime_utc": start_datetime_utc,
            "end_datetime_utc": end_datetime_utc
        }

        return date_utc
    
    def get_time_zone(self,service):
        calendar = service.calendars().get(calendarId='primary').execute()
        timedetail = calendar['timeZone']
        return timedetail
    
    def create_event_dates(self, service, start_date, start_time, end_date, end_time):
        timeZone = self.get_time_zone(service)
        local_tz = pytz.timezone(timeZone)
        gmt_tz = pytz.timezone('GMT')
        if start_date == 'None' and start_time == 'None':
            start_datetime = datetime.now(timezone.utc)
        else:
            if start_date == 'None':
                date = datetime.now().date()
                given_time = datetime.strptime(start_time,"%H:%M:%S")
                given_time = given_time.time()
                start_datetime = datetime.combine(date,given_time)
            elif start_time == 'None':
                given_date = datetime.strptime(start_date, "%Y-%m-%d")
                time_obj = datetime.now(timezone.utc).time()
                start_date = given_date.replace(hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second)
                local_start_date = gmt_tz.localize(start_date)
                start_datetime = local_start_date.astimezone(local_tz)
            else:
                given_date = datetime.strptime(start_date, "%Y-%m-%d")
                given_time = datetime.strptime(start_time, "%H:%M:%S")
                start_datetime = given_date.replace(hour=given_time.hour, minute=given_time.minute, second=given_time.second)
            
        if end_date == 'None' and end_time == 'None':
            end_datetime = start_datetime + timedelta(hours=1)
        else:
            if end_date == 'None':
                date = datetime.now().date()
                given_time = datetime.strptime(start_time,"%H:%M:%S")
                given_time = given_time.time()
                end_datetime = datetime.combine(date,given_time)
            elif end_time == 'None':
                given_date = datetime.strptime(end_date, "%Y-%m-%d")
                time_obj = datetime.now(timezone.utc).time()
                end_date = given_date.replace(hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second)
                local_end_date = gmt_tz.localize(end_date)
                end_datetime = local_end_date.astimezone(local_tz)
            else:
                given_date = datetime.strptime(end_date, "%Y-%m-%d")
                given_time = datetime.strptime(end_time, "%H:%M:%S")
                end_datetime = given_date.replace(hour=given_time.hour, minute=given_time.minute, second=given_time.second)
        
        start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_datetime_utc = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        date_utc = {
            "start_datetime_utc": start_datetime_utc,
            "end_datetime_utc": end_datetime_utc,
            "timeZone": timeZone
        }
        return date_utc