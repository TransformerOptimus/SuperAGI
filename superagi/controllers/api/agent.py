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
from superagi.models.resource import Resource
from superagi.controllers.types.agent_schedule import AgentScheduleInput
from superagi.controllers.types.agent_with_config import AgentConfigInput
from superagi.controllers.types.agent_with_config_schedule import AgentConfigSchedule
from superagi.controllers.types.agent_with_config import AgentConfigExtInput,AgentConfigUpdateExtInput
from jsonmerge import merge
from datetime import datetime
import json
from typing import Optional,List
import pytz
import boto3
from superagi.config.config import get_config
from superagi.models.toolkit import Toolkit
from superagi.models.knowledges import Knowledges

from sqlalchemy import func
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.apm.event_handler import EventHandler

router = APIRouter()

class AgentExecutionIn(BaseModel):
    name: Optional[str]
    goal: Optional[List[str]]
    instruction: Optional[List[str]]

    class Config:
        orm_mode = True

class RunFilterConfigIn(BaseModel):
    run_ids:Optional[List[int]]
    run_status_filter:Optional[str]

    class Config:
        orm_mode = True

class StateChangeConfigIn(BaseModel):
    run_ids:Optional[List[int]]

    class Config:
        orm_mode = True

class RunIDConfig(BaseModel):
    run_ids:List[int]

    class Config:
        orm_mode = True

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
    agent_with_config.project_id=project.id
    agent_with_config.exit="No exit criterion"
    agent_with_config.permission_type="God Mode"
    agent_with_config.LTM_DB=None
    db_agent = Agent.create_agent_with_config(db, agent_with_config)
    
    if agent_with_config.schedule is not None:
        agent_schedule = agent_with_config.schedule
        agent_schedule = AgentSchedule(
            agent_id=db_agent.id,
            start_time=agent_schedule.start_time,
            next_scheduled_time=agent_schedule.start_time,
            recurrence_interval=agent_schedule.recurrence_interval,
            expiry_date=agent_schedule.expiry_date,
            expiry_runs=agent_schedule.expiry_runs,
            current_runs=0,
            status="SCHEDULED"
        )

        agent_schedule.agent_id = db_agent.id
        db.session.add(agent_schedule)
        db.session.commit()

        if agent_schedule.id is None:
            raise HTTPException(status_code=500, detail="Failed to schedule agent")

        agent = db.session.query(Agent).filter(Agent.id == db_agent.id, ).first()
        organisation = agent.get_agent_organisation(db.session)

        EventHandler(session=db.session).create_event('agent_created', {'agent_name': agent_with_config.name,
                                                                            'model': agent_with_config.model}, db_agent.id,
                                                        organisation.id if organisation else 0)

        db.session.commit()
    
        return {
            "agent_id":db_agent.id
        }

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

@router.post("/run/{agent_id}",status_code=201)
def create_run(agent_id:int,agent_execution: AgentExecutionIn,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):
    agent = db.session.query(Agent).filter(Agent.id == agent_id, Agent.is_deleted == False).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    project_id=agent.project_id
    project=db.session.query(Project).filter(Project.id==project_id).first()
    
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    start_step_id = AgentWorkflow.fetch_trigger_step_id(db.session, agent.agent_workflow_id)

    db_agent_execution = db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent_id,AgentExecution.status=="CREATED").first()

    if db_agent_execution is None:
        db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                            agent_id=agent_id, name=agent_execution.name, num_of_calls=0,
                                            num_of_tokens=0,
                                            current_step_id=start_step_id)
        db.session.add(db_agent_execution)
    else:
        db_agent_execution.status = "RUNNING"
    db.session.commit()
    db.session.flush()
    agent_execution_configs={}
    if agent_execution.goal is not None:
        agent_execution_configs = {
            "goal": agent_execution.goal,
        }
    
    if agent_execution.instruction is not None:
        agent_execution_configs["instructions"]=agent_execution.instruction,
    
    if agent_execution_configs != {}:
        AgentExecutionConfiguration.add_or_update_agent_execution_config(session=db.session, execution=db_agent_execution,
                                                                     agent_execution_configs=agent_execution_configs)

    organisation = agent.get_agent_organisation(db.session)
    EventHandler(session=db.session).create_event('run_created', {'agent_execution_id': db_agent_execution.id,'agent_execution_name':db_agent_execution.name},
                                 agent_id, organisation.id if organisation else 0)

    if db_agent_execution.status == "RUNNING":
      execute_agent.delay(db_agent_execution.id, datetime.now())
    return {
        "run_id":db_agent_execution.id
    }

@router.put("/update/{agent_id}")
def update_agent(agent_id: int, agent_with_config: AgentConfigUpdateExtInput,api_key: str = Security(validate_api_key),
                                        organisation:Organisation = Depends(get_organisation_from_api_key)):
    """
        Update an existing Agent

        Args:
            
        Returns:
            Agent: An object of Agent representing the updated Agent.

        Raises:
            HTTPException (Status Code=404): If the Agent or associated Project is not found.
    """

    db_agent = db.session.query(Agent).filter(Agent.id == agent_id, or_(Agent.is_deleted == False, Agent.is_deleted is None)).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")
    
    org_id=organisation.id
    project=db.session.query(Project).filter(Project.organisation_id==org_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_execution=db.session.query(AgentExecution).filter(AgentExecution.agent_id==db_agent.id).first()

    if(db_execution.status=="RUNNING"):
        raise HTTPException(status_code=409, detail="Agent is already running, cannot update")  ## ******
    
    toolkits_arr,tools_arr=get_tool_and_toolkit_arr(agent_with_config.tools,db)
    invalid_tools = Tool.get_invalid_tools(tools_arr, db.session)

    if len(invalid_tools) > 0:  # If the returned value is not True (then it is an invalid tool_id)
        raise HTTPException(status_code=404,
                            detail=f"Tool with IDs {str(invalid_tools)} does not exist. 404 Not Found.")
    
    agent_with_config.tools=tools_arr
    agent_with_config.project_id=project.id
    agent_with_config.exit="No exit criterion"
    agent_with_config.permission_type="God Mode"
    agent_with_config.LTM_DB=None

    for key,value in agent_with_config.dict().items():
        if hasattr(db_agent,key) and value is not None:
            setattr(db_agent,key,value)
        
    db.session.commit()
    db.session.flush()
    
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
    db.session.commit()

    return {
        "agent_id":db_agent.id
    }


@router.get("/run/{agent_id}",status_code=201)
def get_agent_runs(agent_id:int,filter_config:RunFilterConfigIn,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):

    agent = db.session.query(Agent).filter(Agent.id == agent_id, Agent.is_deleted == False).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    project_id=agent.project_id
    project=db.session.query(Project).filter(Project.id==project_id).first()
    
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    db_execution_arr=[]
    if filter_config.run_status_filter is not None:
        filter_config.run_status_filter=filter_config.run_status_filter.upper()

    if filter_config.run_ids is not None and filter_config.run_status_filter is not None and filter_config.run_status_filter in ["CREATED", "RUNNING", "PAUSED", "COMPLETED", "TERMINATED"]:
        db_execution_arr=db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent.id,AgentExecution.id.in_(filter_config.run_ids),AgentExecution.status==filter_config.run_status_filter).all()
    elif filter_config.run_ids is not None:
        db_execution_arr=db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent.id,AgentExecution.id.in_(filter_config.run_ids)).all()
    elif filter_config.run_status_filter is not None and filter_config.run_status_filter in ["CREATED", "RUNNING", "PAUSED", "COMPLETED", "TERMINATED"]:
        db_execution_arr=db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent.id,AgentExecution.status==filter_config.run_status_filter).all()
    else:
        db_execution_arr=db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent_id)
    
    response_arr=[]
    for ind_execution in db_execution_arr:
        response_arr.append({"run_id":ind_execution.id, "status":ind_execution.status})

    return response_arr


@router.get("/pause/{agent_id}",status_code=201)
def pause_agent_runs(agent_id:int,state_config:StateChangeConfigIn,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):

    agent = db.session.query(Agent).filter(Agent.id == agent_id, Agent.is_deleted == False).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    project_id=agent.project_id
    project=db.session.query(Project).filter(Project.id==project_id).first()
    
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    db_execution_arr=[]
    
    if state_config.run_ids is not None:
        db_execution_arr=db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent.id,AgentExecution.status=="RUNNING",AgentExecution.id.in_(state_config.run_ids)).all()
    else:
        db_execution_arr=db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent.id,AgentExecution.status=="RUNNING").all()
    for ind_execution in db_execution_arr:
        ind_execution.status="PAUSED"
    db.session.commit()
    return {
        "result":"success"
    }

@router.get("/resume/{agent_id}",status_code=201)
def resume_agent_runs(agent_id:int,state_config:StateChangeConfigIn,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):

    agent = db.session.query(Agent).filter(Agent.id == agent_id, Agent.is_deleted == False).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    project_id=agent.project_id
    project=db.session.query(Project).filter(Project.id==project_id).first()
    
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    db_execution_arr=[]
    
    if state_config.run_ids is not None:
        db_execution_arr=db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent.id,AgentExecution.status=="PAUSED",AgentExecution.id.in_(state_config.run_ids)).all()
    else:
        db_execution_arr=db.session.query(AgentExecution).filter(AgentExecution.agent_id==agent.id,AgentExecution.status=="PAUSED").all()
    for ind_execution in db_execution_arr:
        ind_execution.status="RUNNING"
    db.session.commit()
    return {
        "result":"success"
    }

@router.get("/resources/output",status_code=201)
def get_run_resources(run_id_config:RunIDConfig,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):
    run_ids_arr=run_id_config.run_ids
    if len(run_ids_arr)==0:  
        raise HTTPException(status_code=404,
                            detail=f"No execution_id found")
    response_obj={}
    s3 = boto3.client(
        's3',
        aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
    )

    for run_id in run_ids_arr:
        run_id_file_urls=[]
        db_execution=db.session.query(AgentExecution).filter(AgentExecution.id==run_id).first()

        if db_execution is None:
            raise HTTPException(status_code=404, detail=f"Run ID {run_id} not found")
        
        agent_id=db_execution.agent_id
        db_agent=db.session.query(Agent).filter(Agent.id==agent_id).first()
        project_id=db_agent.project_id
        project=db.session.query(Project).filter(Project.id==project_id).first()

        if project.organisation_id!=organisation.id:
            raise HTTPException(status_code=404, detail=f"Run ID {run_id} not found")
        
        files=db.session.query(Resource).filter(Resource.agent_execution_id==run_id).all()
        for file in files:
            response = s3.get_object(Bucket=get_config("BUCKET_NAME"), Key=file.path)
            content = response["Body"].read()
            bucket_name = get_config("INSTAGRAM_TOOL_BUCKET_NAME")
            file_name=file.path.split('/')[-1]
            file_name=''.join(char for char in file_name if char != "`")
            object_key=f"public_resources/run_id{run_id}/{file_name}"
            s3.put_object(Bucket=bucket_name, Key=object_key, Body=content)
            file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
            run_id_file_urls.append(file_url)

        response_obj["run_id_"+str(run_id)]=run_id_file_urls
        

    return response_obj

def get_tool_and_toolkit_arr(agent_config_tools_arr,db):
    toolkits_arr=set()
    tools_arr=set()

    for tool_obj in agent_config_tools_arr:
        toolkit=db.session.query(Toolkit).filter(Toolkit.name==tool_obj["name"].strip()).first()
        if toolkit is None:
            raise HTTPException(status_code=404,
                            detail=f"One or more of the Toolkit(s) does not exist. 404 Not Found.")
        toolkits_arr.add(toolkit.id)
        if tool_obj.get("tools"):
            for tool_name_str in tool_obj["tools"]:
                tool_db_obj=db.session.query(Tool).filter(Tool.name==tool_name_str.strip()).first()
                # if tool_db_obj is None:
                #     raise HTTPException(status_code=404,
                #                     detail=f"One or more of the Tool(s) does not exist. 404 Not Found.")
                tools_arr.add(tool_db_obj.id)
        else:
            tools=db.session.query(Tool).filter(Tool.toolkit_id==toolkit.id).all()
            # if tool_db_obj is None:
            #         raise HTTPException(status_code=404,
            #                         detail=f"One or more of the Tool(s) does not exist. 404 Not Found.")
            for tool_db_obj in tools:
                tools_arr.add(tool_db_obj.id)
    return list(toolkits_arr),list(tools_arr)