from fastapi import Depends, Query
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from sqlalchemy.orm import sessionmaker

import superagi
import json
from superagi.models.db import connect_db
import http.client as http_client
from superagi.helper.twitter_tokens import TwitterTokens
from superagi.helper.auth import get_current_user
from superagi.models.tool_config import ToolConfig
from superagi.models.toolkit import Toolkit
from superagi.models.oauth_tokens import OauthTokens

router = APIRouter()

@router.get('/oauth-tokens')
async def twitter_oauth(oauth_token: str = Query(...),oauth_verifier: str = Query(...), Authorize: AuthJWT = Depends()):
    print("///////////////////////////")
    print(oauth_token)
    token_uri = f'https://api.twitter.com/oauth/access_token?oauth_verifier={oauth_verifier}&oauth_token={oauth_token}'
    conn = http_client.HTTPSConnection("api.twitter.com")
    conn.request("POST", token_uri, "")
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    frontend_url = superagi.config.config.get_config("FRONTEND_URL", "http://localhost:3000")
    redirect_url_success = f"{frontend_url}/twitter_creds/?{response_data}"
    return RedirectResponse(url=redirect_url_success)

@router.post("/send_twitter_creds/{twitter_creds}")
def send_twitter_tool_configs(twitter_creds: str, Authorize: AuthJWT = Depends()):
    current_user = get_current_user()
    user_id = current_user.id
    credentials = json.loads(twitter_creds)
    credentials["user_id"] = user_id
    toolkit = db.session.query(Toolkit).filter(Toolkit.id == credentials["toolkit_id"]).first()
    api_key = db.session.query(ToolConfig).filter(ToolConfig.key == "TWITTER_API_KEY", ToolConfig.toolkit_id == credentials["toolkit_id"]).first()
    api_key_secret = db.session.query(ToolConfig).filter(ToolConfig.key == "TWITTER_API_SECRET", ToolConfig.toolkit_id == credentials["toolkit_id"]).first()
    final_creds = {
        "api_key": api_key.value,
        "api_key_secret": api_key_secret.value,
        "oauth_token": credentials["oauth_token"],
        "oauth_token_secret": credentials["oauth_token_secret"]
    }
    tokens = OauthTokens().add_or_update(db.session, credentials["toolkit_id"], user_id, toolkit.organisation_id, "TWITTER_OAUTH_TOKENS", str(final_creds))
    if tokens:
        success = True
    else:
        success = False
    return success

@router.get("/get_twitter_creds/toolkit_id/{toolkit_id}")
def get_twitter_tool_configs(toolkit_id: int):
    twitter_config_key = db.session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit_id,ToolConfig.key == "TWITTER_API_KEY").first()
    twitter_config_secret = db.session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit_id,ToolConfig.key == "TWITTER_API_SECRET").first()
    api_data =  {
        "api_key": twitter_config_key.value,
        "api_secret": twitter_config_secret.value
    }
    response = TwitterTokens(db.session).get_request_token(api_data)
    return response