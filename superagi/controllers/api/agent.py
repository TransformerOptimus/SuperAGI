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
from superagi.helper.auth import check_auth,validate_api_key,get_organisation_from_api_key
from superagi.models.agent import Agent
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_schedule import AgentSchedule
from superagi.models.agent_template import AgentTemplate
from superagi.models.project import Project
from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.agent_execution import AgentExecution
from superagi.models.tool import Tool
from superagi.models.api_key import ApiKey
from superagi.models.organisation import Organisation
from superagi.controllers.types.agent_schedule import AgentScheduleInput
from superagi.controllers.types.agent_with_config import AgentConfigInput
from superagi.controllers.types.agent_with_config_schedule import AgentConfigSchedule
from superagi.controllers.types.agent_with_config import AgentConfigExtInput
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
@router.post("/",status_code=201)
def create_agent(api_key: str = Security(validate_api_key)):
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

    return "db_agent"

@router.post("/add",status_code=201)
def create_agent_with_config(agent_with_config: AgentConfigExtInput,
                             api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):
    """
    Create a new agent with configurations.

    Args:
        agent_with_config (AgentConfigInput): Data for creating a new agent with configurations.
            - name (str): Name of the agent.
            - description (str): Description of the agent.
            - goal (List[str]): List of goals for the agent.
            - agent_type (str): Type of the agent.
            - constraints (List[str]): List of constraints for the agent.
            - tools (List[int]): List of tool identifiers associated with the agent.
            - exit (str): Exit condition for the agent.
            - iteration_interval (int): Interval between iterations for the agent.
            - model (str): Model information for the agent.
            - permission_type (str): Permission type for the agent.
            - LTM_DB (str): LTM database for the agent.
            - max_iterations (int): Maximum number of iterations for the agent.
            - user_timezone (string): Timezone of the user

    Returns:
        dict: Dictionary containing the created agent's ID, execution ID, name, and content type.

    Raises:
        HTTPException (status_code=404): If the associated project or any of the tools is not found.
"""
    org_id=organisation.id
    project=db.session.query(Project).filter(Project.organisation_id==org_id).first()
    toolkits_arr,tools_arr=get_tool_and_toolkit_arr(agent_with_config.tools,db)
    invalid_tools = Tool.get_invalid_tools(tools_arr, db.session)
    if len(invalid_tools) > 0:  # If the returned value is not True (then it is an invalid tool_id)
        raise HTTPException(status_code=404,
                            detail=f"Tool with IDs {str(invalid_tools)} does not exist. 404 Not Found.")
    
    agent_toolkit_tools = Toolkit.fetch_tool_ids_from_toolkit(session=db.session,
                                                              toolkit_ids=toolkits_arr)
    agent_with_config.tools=tools_arr
    print("xxxxxxxxxx",tools_arr)
    agent_with_config.project_id=project.id
    agent_with_config.exit="No exit criterion"
    agent_with_config.permission_type="God Mode"
    agent_with_config.LTM_DB=None
    db_agent = Agent.create_agent_with_config(db, agent_with_config)

    start_step_id = AgentWorkflow.fetch_trigger_step_id(db.session, db_agent.agent_workflow_id)
    # Creating an execution with RUNNING status
    execution = AgentExecution(status='CREATED', last_execution_time=datetime.now(), agent_id=db_agent.id,
                               name="New Run", current_step_id=start_step_id)

    agent_execution_configs = {
        "goal": agent_with_config.goal,
        "instruction": agent_with_config.instruction
    }
    db.session.add(execution)
    db.session.commit()
    db.session.flush()
    AgentExecutionConfiguration.add_or_update_agent_execution_config(session=db.session, execution=execution,
                                                                     agent_execution_configs=agent_execution_configs)

    agent = db.session.query(Agent).filter(Agent.id == db_agent.id, ).first()
    organisation = agent.get_agent_organisation(db.session)
    EventHandler(session=db.session).create_event('agent_created', {'agent_name': agent_with_config.name,
                                                                    'model': agent_with_config.model}, db_agent.id,
                                                  organisation.id if organisation else 0)

    # execute_agent.delay(execution.id, datetime.now())

    db.session.commit()
    return {
        "agent_id":db_agent.id
    }


def get_tool_and_toolkit_arr(agent_config_tools_arr,db):
    toolkits_arr=set()
    tools_arr=set()

    for tool_obj in agent_config_tools_arr:
        toolkit=db.session.query(Toolkit).filter(Toolkit.name==tool_obj["name"].strip()).first()
        toolkits_arr.add(toolkit.id)
        if tool_obj.get("tools"):
            for tool_name_str in tool_obj["tools"]:
                tool_db_obj=db.session.query(Tool).filter(Tool.name==tool_name_str.strip()).first()
                tools_arr.add(tool_db_obj.id)
        else:
            tools=db.session.query(Tool).filter(Tool.toolkit_id==toolkit.id).all()
            for tool_db_obj in tools:
                tools_arr.add(tool_db_obj.id)
    print("(((((((((",toolkits_arr,tools_arr)
    return list(toolkits_arr),list(tools_arr)
