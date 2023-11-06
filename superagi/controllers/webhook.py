from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
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
    filters: dict

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
    filters: dict

    class Config:
        orm_mode = True

class WebHookEdit(BaseModel):
    url: str
    filters: dict

    class Config:
        orm_mode = True



# CRUD Operations`
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
                          is_deleted=False, filters=webhook.filters)
    db.session.add(db_webhook)
    db.session.commit()
    db.session.flush()
    return db_webhook

@router.get("/get", response_model=Optional[WebHookOut])
def get_all_webhooks(
    Authorize: AuthJWT = Depends(check_auth),
    organisation=Depends(get_user_organisation),
):
    """
    Retrieves a single webhook for the authenticated user's organisation.

    Returns:
        JSONResponse: A JSON response containing the retrieved webhook.

    Raises:
    """
    webhook = db.session.query(Webhooks).filter(Webhooks.org_id == organisation.id, Webhooks.is_deleted == False).first()
    return webhook

@router.post("/edit/{webhook_id}", response_model=WebHookOut)
def edit_webhook(
    updated_webhook: WebHookEdit,
    webhook_id: int,
    Authorize: AuthJWT = Depends(check_auth),
    organisation=Depends(get_user_organisation),
):
    """
    Soft-deletes a webhook by setting the value of is_deleted to True.

    Args:
        webhook_id (int): The ID of the webhook to delete.

    Returns:
        WebHookOut: The deleted webhook.

    Raises:
        HTTPException (Status Code=404): If the webhook is not found.
    """
    webhook = db.session.query(Webhooks).filter(Webhooks.org_id == organisation.id, Webhooks.id == webhook_id, Webhooks.is_deleted == False).first()
    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhook.url = updated_webhook.url
    webhook.filters = updated_webhook.filters

    db.session.commit()

    return webhook