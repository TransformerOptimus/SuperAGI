from fastapi import Depends, Query
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

import superagi
import json
import requests
from datetime import datetime, timedelta
from superagi.models.db import connect_db
import http.client as http_client
from superagi.helper.auth import get_current_user, check_auth
from superagi.models.tool_config import ToolConfig
from superagi.models.toolkit import Toolkit
from superagi.models.oauth_tokens import OauthTokens
from superagi.config.config import get_config
from superagi.helper.encyption_helper import decrypt_data, is_encrypted

router = APIRouter()

@router.get('/oauth-tokens')
async def google_auth_calendar(code: str = Query(...), state: str = Query(...)):
    toolkit_id = int(state)
    client_id = db.session.query(ToolConfig).filter(ToolConfig.key == "GOOGLE_CLIENT_ID", ToolConfig.toolkit_id == toolkit_id).first()
    if(is_encrypted(client_id.value)):
        client_id = decrypt_data(client_id.value)
    else:
        client_id = client_id.value
    client_secret = db.session.query(ToolConfig).filter(ToolConfig.key == "GOOGLE_CLIENT_SECRET", ToolConfig.toolkit_id == toolkit_id).first()
    if(is_encrypted(client_secret.value)):
        client_secret = decrypt_data(client_secret.value)
    else:
        client_secret = client_secret.value
    token_uri = 'https://oauth2.googleapis.com/token'
    scope = 'https://www.googleapis.com/auth/calendar'
    env = get_config("ENV", "DEV")
    if env == "DEV":
        redirect_uri = "http://localhost:3000/api/google/oauth-tokens"
    else:
        redirect_uri = "https://app.superagi.com/api/google/oauth-tokens"
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'grant_type': 'authorization_code',
        'code': code,
        'access_type': 'offline',
        'approval_prompt': 'force'
    }
    response = requests.post(token_uri, data=params)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Client Secret")
    response = response.json()
    expire_time = datetime.utcnow() + timedelta(seconds=response['expires_in'])
    expire_time = expire_time - timedelta(minutes=5)
    response['expiry'] = expire_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    response_data = json.dumps(response)
    frontend_url = superagi.config.config.get_config("FRONTEND_URL", "http://localhost:3000")
    redirect_url_success = f"{frontend_url}/google_calendar_creds/?{response_data}"
    return RedirectResponse(url=redirect_url_success)

@router.post("/send_google_creds/toolkit_id/{toolkit_id}")
def send_google_calendar_configs(google_creds: dict, toolkit_id: int, Authorize: AuthJWT = Depends(check_auth)):
    engine = connect_db()
    Session = sessionmaker(bind=engine)
    session = Session()
    current_user = get_current_user(Authorize)
    user_id = current_user.id
    toolkit = db.session.query(Toolkit).filter(Toolkit.id == toolkit_id).first()
    google_creds = json.dumps(google_creds)
    print(google_creds)
    tokens = OauthTokens().add_or_update(session, toolkit_id, user_id, toolkit.organisation_id, "GOOGLE_CALENDAR_OAUTH_TOKENS", google_creds)
    if tokens:
        success = True
    else:
        success = False
    return success


@router.get("/get_google_creds/toolkit_id/{toolkit_id}")
def get_google_calendar_tool_configs(toolkit_id: int):
    google_calendar_config = db.session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit_id,
                                                                 ToolConfig.key == "GOOGLE_CLIENT_ID").first()
    if is_encrypted(google_calendar_config.value):
        google_calendar_config.value = decrypt_data(google_calendar_config.value)
    return {
        "client_id": google_calendar_config.value
    }
