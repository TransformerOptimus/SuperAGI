import json
import uuid
import secrets
from datetime import datetime       
from fastapi import APIRouter, Body
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel
from superagi.helper.auth import get_user_organisation
from superagi.helper.auth import check_auth
from superagi.models.api_key import ApiKey
from typing import Optional, Annotated
router = APIRouter()



@router.post("/")
def create_api_key(name: Annotated[str,Body(embed=True)], Authorize: AuthJWT = Depends(check_auth), organisation=Depends(get_user_organisation)):
    api_key=str(uuid.uuid4())
    obj=ApiKey(key=api_key,name=name,org_id=organisation.id)
    db.session.add(obj)
    db.session.commit()
    return api_key
