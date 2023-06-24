from datetime import datetime, timedelta, timezone

import pytz


class CalendarDate:
    def create_event_dates(self, service, start_date, start_time, end_date, end_time):
        local_tz = pytz.timezone(self._get_time_zone(service))
        start_datetime, end_datetime = self._localize_daterange(start_date, end_date, start_time, end_time, local_tz)
        date_utc = {
            "start_datetime_utc": self._datetime_to_string(start_datetime, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "end_datetime_utc": self._datetime_to_string(end_datetime, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "timeZone": self._get_time_zone(service)
        }
        return date_utc

    def get_date_utc(self, start_date, end_date, start_time, end_time, service):
        local_tz = pytz.timezone(self._get_time_zone(service))
        start_datetime, end_datetime = self._localize_daterange(start_date, end_date, start_time, end_time, local_tz)
        date_utc = {
            "start_datetime_utc": self._datetime_to_string(start_datetime, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "end_datetime_utc": self._datetime_to_string(end_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")
        }
        return date_utc

    def _get_time_zone(self, service):
        calendar = service.calendars().get(calendarId='primary').execute()
        time_detail = calendar['timeZone']
        return time_detail

    def _convert_to_utc(self, date_time, local_tz):
        local_datetime = local_tz.localize(date_time)
        gmt_tz = pytz.timezone("GMT")
        return local_datetime.astimezone(gmt_tz)

    def _string_to_datetime(self, date_str, date_format):
        return datetime.strptime(date_str, date_format) if date_str else None

    def _localize_daterange(self, start_date, end_date, start_time, end_time, local_tz):
        start_datetime = self._string_to_datetime(start_date, "%Y-%m-%d") if start_date != 'None' else datetime.now(
            timezone.utc)
        end_datetime = self._string_to_datetime(end_date,
                                                "%Y-%m-%d") if end_date != 'None' else start_datetime + timedelta(
            days=30) - timedelta(microseconds=1)
        time_obj_start = self._string_to_datetime(start_time, "%H:%M:%S")
        time_obj_end = self._string_to_datetime(end_time, "%H:%M:%S")
        start_datetime = start_datetime.replace(hour=time_obj_start.hour, minute=time_obj_start.minute,
                                                second=time_obj_start.second,
                                                microsecond=0) if time_obj_start else start_datetime.replace(hour=0,
                                                                                                             minute=0,
                                                                                                             second=0,
                                                                                                             microsecond=0)
        end_datetime = end_datetime.replace(hour=time_obj_end.hour, minute=time_obj_end.minute,
                                            second=time_obj_end.second) if time_obj_end else end_datetime.replace(
            hour=23, minute=59, second=59, microsecond=999999)
        return self._convert_to_utc(start_datetime, local_tz), self._convert_to_utc(end_datetime, local_tz)

    def _datetime_to_string(self, date_time, date_format):
        return date_time.strftime(date_format) if date_time else None
