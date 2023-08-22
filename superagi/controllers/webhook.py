from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel

# from superagi.types.db import AgentOut, AgentIn
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.models.webhooks import Webhooks

router = APIRouter()


class WebHookIn(BaseModel):
    name: str
    url: str
    headers: dict

    class Config:
        orm_mode = True


class WebHookOut(BaseModel):
    id: int
    org_id: int
    name: str
    url: str
    headers: dict
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# CRUD Operations
@router.post("/add", response_model=WebHookOut, status_code=201)
def create_webhook(webhook: WebHookIn, Authorize: AuthJWT = Depends(check_auth),
                   organisation=Depends(get_user_organisation)):
    """
        Creates a new webhook

        Args:
            
        Returns:
            Agent: An object of Agent representing the created Agent.

        Raises:
            HTTPException (Status Code=404): If the associated project is not found.
    """
    db_webhook = Webhooks(name=webhook.name, url=webhook.url, headers=webhook.headers, org_id=organisation.id,
                          is_deleted=False)
    db.session.add(db_webhook)
    db.session.commit()
    db.session.flush()

    return db_webhook
