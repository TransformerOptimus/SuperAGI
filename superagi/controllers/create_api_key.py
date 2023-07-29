import json
import uuid
import secrets
from datetime import datetime       
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from superagi.helper.auth import check_auth

router = APIRouter()

@router.get("/")
def create_api_key(Authorize: AuthJWT = Depends(check_auth)):
    api_key=str(uuid.uuid4())
    return api_key
