import pickle
import os
import json
import ast
from  datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from superagi.config.config import get_config
from googleapiclient.discovery import build
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from sqlalchemy.orm import Session
from superagi.models.tool_config import ToolConfig
from superagi.resource_manager.file_manager import FileManager
from superagi.models.toolkit import Toolkit
from superagi.models.oauth_tokens import OauthTokens
from superagi.helper.encyption_helper import decrypt_data, is_encrypted

class GoogleCalendarCreds:

    def __init__(self, session: Session):
        self.session = session

    def get_credentials(self, toolkit_id):
        toolkit = self.session.query(Toolkit).filter(Toolkit.id == toolkit_id).first()
        organisation_id = toolkit.organisation_id
        google_creds = self.session.query(OauthTokens).filter(OauthTokens.toolkit_id == toolkit_id, OauthTokens.organisation_id == organisation_id).first()
        if google_creds:
            user_id = google_creds.user_id
            final_creds = json.loads(google_creds.value)
            final_creds["refresh_token"] = self.fix_refresh_token(final_creds["refresh_token"])
            expire_time = datetime.strptime(final_creds["expiry"], "%Y-%m-%dT%H:%M:%S.%fZ")
            google_creds = self.session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit_id).all()
            client_id = ""
            client_secret = ""
            for credentials in google_creds:
                credentials = credentials.__dict__
                if credentials["key"] == "GOOGLE_CLIENT_ID":
                    if is_encrypted(credentials["value"]):
                        client_id = decrypt_data(credentials["value"])
                    else:
                        client_id = credentials["value"]
                if credentials["key"] == "GOOGLE_CLIENT_SECRET":
                    if is_encrypted(credentials["value"]):
                        client_secret = decrypt_data(credentials["value"])
                    else:
                        client_secret = credentials["value"]
            creds = Credentials.from_authorized_user_info(info={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": final_creds["refresh_token"],
                "scopes": "https://www.googleapis.com/auth/calendar"
            })
            if expire_time > datetime.utcnow():
                creds.refresh(Request())
                creds_json = creds.to_json()
                tokens = OauthTokens().add_or_update(self.session, toolkit_id, user_id, toolkit.organisation_id, "GOOGLE_CALENDAR_OAUTH_TOKENS", str(creds_json))
        else:
            return {"success": False}
        service = build('calendar','v3',credentials=creds)
        return {"success": True, "service": service}
    
    def fix_refresh_token(self, refresh_token):
        if refresh_token.count('/') == 1:
            # Find the position of '/'
            slash_index = refresh_token.index('/')
            # Insert one more '/' at the position
            refresh_token = refresh_token[:slash_index+1] + '/' + refresh_token[slash_index+1:]
        return refresh_token