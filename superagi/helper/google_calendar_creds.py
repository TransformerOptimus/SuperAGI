import os
from typing import Any, List, Optional, Union
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from superagi.config.config import get_config


class GoogleCalendarCreds:
    def get_credentials(self):
        scope = "https://www.googleapis.com/auth/calendar"
        file_name = "credential_token.json"
        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
        file_path = file_name
        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            file_path = root_dir + file_name
        else:
            file_path = os.getcwd() + "/" + file_name
        if os.path.exists(file_path):
            creds = Credentials.from_authorized_user_file(file_path, scope)
        else:
            return {'success': False}
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("-------------------------------------")
                creds.refresh(Request())
        with open(file_path, "w") as file:
            file.write(creds.to_json())
        print("///////////////////////////////////////////")
        print(creds)
        service = build("calendar","v3",credentials=creds)
        return {"success": True, "service": service}
