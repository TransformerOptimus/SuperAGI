import json
from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException, Depends ,Security
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel

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
from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.agent_execution import AgentExecution
from superagi.models.tool import Tool
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


class AgentOut(BaseModel):
    id: int
    name: str
    project_id: int
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AgentIn(BaseModel):
    name: str
    project_id: int
    description: str

    class Config:
        orm_mode = True


# CRUD Operations
@router.post("/add", status_code=201)
def create_agent(agent: AgentIn,api_key: str = Security(validate_api_key)):
    """
        Creates a new Agent

        Args:
            agent (Agent): An object representing the Agent to be created.
                Contains the following attributes:
                - name (str): Name of the Agent
                - project_id (int): Identifier of the associated project
                - description (str): Description of the Agent
                - agent_workflow_id (int): Identifier of the Agent Workflow in use

        Returns:
            Agent: An object of Agent representing the created Agent.

        Raises:
            HTTPException (Status Code=404): If the associated project is not found.
    """

    # project = db.session.query(Project).get(agent.project_id)

    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")

    # db_agent = Agent(name=agent.name, description=agent.description, project_id=agent.project_id)
    # db.session.add(db_agent)
    # db.session.commit()
    return "db_agent"
