import pickle
import os
import json
from  datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from superagi.config.config import get_config
from googleapiclient.discovery import build

class GoogleCalendarCreds:
    def get_credentials(self):
        file_name = "credential_token.pickle"
        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
        file_path = file_name
        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            file_path = root_dir + file_name
        else:
            file_path = os.getcwd() + "/" + file_name
        if os.path.exists(file_path):
            with open(file_path,'rb') as file:
                creds = pickle.load(file)
            if isinstance(creds, str):
                creds = json.loads(creds)
            expire_time = datetime.strptime(creds["expiry"], "%Y-%m-%dT%H:%M:%S.%fZ")
            creds = Credentials.from_authorized_user_info(info={
                "client_id": get_config("GOOGLE_CLIENT_ID"),
                "client_secret": get_config("GOOGLE_CLIENT_SECRET"),
                "refresh_token": creds["refresh_token"],
                "scopes": "https://www.googleapis.com/auth/calendar"
            })
            if expire_time < datetime.utcnow():
                creds.refresh(Request())
                creds_json = creds.to_json()
                with open(file_path,'wb') as file:
                    pickle.dump(creds_json,file)

        else:
            return {"success": False}
        
        service = build('calendar','v3',credentials=creds)
        return {"success": True, "service": service}
            

