import json
from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException, Depends ,Security
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel,Json

from jsonmerge import merge
from pytz import timezone
from sqlalchemy import func, or_
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.worker import execute_agent
from superagi.helper.auth import check_auth,validate_api_key
from superagi.models.agent import Agent
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_schedule import AgentSchedule
from superagi.models.agent_template import AgentTemplate
from superagi.models.project import Project
from superagi.models.agent_execution import AgentExecution
from superagi.models.tool import Tool
from superagi.models.web_hooks import WebHooks
from superagi.controllers.types.agent_schedule import AgentScheduleInput
from superagi.controllers.types.agent_with_config import AgentConfigInput
from superagi.controllers.types.agent_with_config_schedule import AgentConfigSchedule
from jsonmerge import merge
from datetime import datetime
import json

from superagi.models.toolkit import Toolkit
from superagi.models.knowledges import Knowledges

from sqlalchemy import func
# from superagi.types.db import AgentOut, AgentIn
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.apm.event_handler import EventHandler

router = APIRouter()


class WebHookIn(BaseModel):
    name: str
    url : str
    headers : dict

    class Config:
        orm_mode = True

class WebHookOut(BaseModel):
    id: int
    org_id: int
    name: str
    url: str
    headers: dict
    isDeleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# CRUD Operations
@router.post("/add",response_model=WebHookOut ,status_code=201)
def create_webhook(webhook: WebHookIn,Authorize: AuthJWT = Depends(check_auth),organisation=Depends(get_user_organisation)):
    """
        Creates a new webhook

        Args:
            
        Returns:
            Agent: An object of Agent representing the created Agent.

        Raises:
            HTTPException (Status Code=404): If the associated project is not found.
    """
    db_webhook=WebHooks(name=webhook.name,url=webhook.url,headers=webhook.headers,org_id=organisation.id,isDeleted=False)
    db.session.add(db_webhook)
    db.session.commit()
    db.session.flush()

    return db_webhook
