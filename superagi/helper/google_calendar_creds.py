import pickle
import os
import json
from  datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from superagi.config.config import get_config
from googleapiclient.discovery import build
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.models.tool_config import ToolConfig
from superagi.resource_manager.file_manager import FileManager

class GoogleCalendarCreds:

    def get_credentials(self, toolkit_id):
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
            engine = connect_db()
            Session = sessionmaker(bind=engine)
            session = Session()
            resource_manager: FileManager = None
            with open(file_path,'rb') as file:
                creds = pickle.load(file)
            if isinstance(creds, str):
                creds = json.loads(creds)
            expire_time = datetime.strptime(creds["expiry"], "%Y-%m-%dT%H:%M:%S.%fZ")
            google_creds = session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit_id).all()
            client_id = ""
            client_secret = ""
            for credentials in google_creds:
                credentials = credentials.__dict__
                if credentials["key"] == "GOOGLE_CLIENT_ID":
                    client_id = credentials["value"]
                if credentials["key"] == "GOOGLE_CLIENT_SECRET":
                    client_secret = credentials["value"]
            creds = Credentials.from_authorized_user_info(info={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": creds["refresh_token"],
                "scopes": "https://www.googleapis.com/auth/calendar"
            })
            if expire_time < datetime.utcnow():
                creds.refresh(Request())
                creds_json = creds.to_json()
                resource_manager.write_file(file_name, creds_json)
        else:
            return {"success": False}
        service = build('calendar','v3',credentials=creds)
        return {"success": True, "service": service}

