from fastapi import APIRouter
from fastapi import HTTPException, Depends ,Security

from fastapi_sqlalchemy import db
from pydantic import BaseModel

from superagi.worker import execute_agent
from superagi.helper.auth import validate_api_key,get_organisation_from_api_key
from superagi.models.agent import Agent
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_schedule import AgentSchedule
from superagi.models.project import Project
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.agent_execution import AgentExecution
from superagi.models.organisation import Organisation
from superagi.models.resource import Resource
from superagi.controllers.types.agent_with_config import AgentConfigExtInput,AgentConfigUpdateExtInput
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.helper.s3_helper import S3Helper
from datetime import datetime
from typing import Optional,List
from superagi.models.toolkit import Toolkit
from superagi.apm.event_handler import EventHandler
from superagi.config.config import get_config
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

class ExecutionStateChangeConfigIn(BaseModel):
    run_ids:Optional[List[int]]

    class Config:
        orm_mode = True

class RunIDConfig(BaseModel):
    run_ids:List[int]

    class Config:
        orm_mode = True

@router.post("", status_code=200)
def create_agent_with_config(agent_with_config: AgentConfigExtInput,
                             api_key: str = Security(validate_api_key), organisation:Organisation = Depends(get_organisation_from_api_key)):
    project=Project.find_by_org_id(db.session, organisation.id)
    try:
        tools_arr=Toolkit.get_tool_and_toolkit_arr(db.session,organisation.id,agent_with_config.tools)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    agent_with_config.tools=tools_arr
    agent_with_config.project_id=project.id
    agent_with_config.exit="No exit criterion"
    agent_with_config.permission_type="God Mode"
    agent_with_config.LTM_DB=None
    db_agent = Agent.create_agent_with_config(db, agent_with_config)

    if agent_with_config.schedule is not None:
        agent_schedule = AgentSchedule.save_schedule_from_config(db.session, db_agent, agent_with_config.schedule)
        if agent_schedule is None:
            raise HTTPException(status_code=500, detail="Failed to schedule agent")
        EventHandler(session=db.session).create_event('agent_created', {'agent_name': agent_with_config.name,
                                                                            'model': agent_with_config.model}, db_agent.id,
                                                        organisation.id if organisation else 0)
        db.session.commit()
        return {
            "agent_id": db_agent.id
        }
    
    start_step = AgentWorkflow.fetch_trigger_step_id(db.session, db_agent.agent_workflow_id)
    iteration_step_id = IterationWorkflow.fetch_trigger_step_id(db.session,
                                                                start_step.action_reference_id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1
    # Creating an execution with RUNNING status
    execution = AgentExecution(status='CREATED', last_execution_time=datetime.now(), agent_id=db_agent.id,
                               name="New Run", current_agent_step_id=start_step.id, iteration_workflow_step_id=iteration_step_id)
    agent_execution_configs = {
        "goal": agent_with_config.goal,
        "instruction": agent_with_config.instruction
    }
    db.session.add(execution)
    db.session.commit()
    db.session.flush()
    AgentExecutionConfiguration.add_or_update_agent_execution_config(session=db.session, execution=execution,
                                                                     agent_execution_configs=agent_execution_configs)

    organisation = db_agent.get_agent_organisation(db.session)
    EventHandler(session=db.session).create_event('agent_created', {'agent_name': agent_with_config.name,
                                                                    'model': agent_with_config.model}, db_agent.id,
                                                  organisation.id if organisation else 0)
    # execute_agent.delay(execution.id, datetime.now())
    db.session.commit()
    return {
        "agent_id": db_agent.id
    }

@router.post("/{agent_id}/run",status_code=200)
def create_run(agent_id:int,agent_execution: AgentExecutionIn,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):
    agent=Agent.get_agent_from_id(db.session,agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    project=Project.find_by_id(db.session, agent.project_id)
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    db_schedule=AgentSchedule.find_by_agent_id(db.session, agent_id)
    if db_schedule is not None:
        raise HTTPException(status_code=409, detail="Agent is already scheduled,cannot run")
    start_step_id = AgentWorkflow.fetch_trigger_step_id(db.session, agent.agent_workflow_id)
    db_agent_execution=AgentExecution.get_execution_by_agent_id_and_status(db.session, agent_id, "CREATED")

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

    agent_execution_configs = {}
    if agent_execution.goal is not None:
        agent_execution_configs = {
            "goal": agent_execution.goal,
        }

    if agent_execution.instruction is not None:
        agent_execution_configs["instructions"] = agent_execution.instruction,

    if agent_execution_configs != {}:
        AgentExecutionConfiguration.add_or_update_agent_execution_config(session=db.session, execution=db_agent_execution,
                                                                     agent_execution_configs=agent_execution_configs)
    EventHandler(session=db.session).create_event('run_created', {'agent_execution_id': db_agent_execution.id,'agent_execution_name':db_agent_execution.name},
                                 agent_id, organisation.id if organisation else 0)

    if db_agent_execution.status == "RUNNING":
      execute_agent.delay(db_agent_execution.id, datetime.now())
    return {
        "run_id":db_agent_execution.id
    }

@router.put("/{agent_id}",status_code=200)
def update_agent(agent_id: int, agent_with_config: AgentConfigUpdateExtInput,api_key: str = Security(validate_api_key),
                                        organisation:Organisation = Depends(get_organisation_from_api_key)):
    
    db_agent= Agent.get_active_agent_by_id(db.session, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")
    
    project=Project.find_by_id(db.session, db_agent.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    # db_execution=AgentExecution.get_execution_by_agent_id_and_status(db.session, agent_id, "RUNNING")
    # if db_execution is not None:
    #     raise HTTPException(status_code=409, detail="Agent is already running,please pause and then update")
     
    db_schedule=AgentSchedule.find_by_agent_id(db.session, agent_id)
    if db_schedule is not None:
        raise HTTPException(status_code=409, detail="Agent is already scheduled,cannot update")
    
    try:
        tools_arr=Toolkit.get_tool_and_toolkit_arr(db.session,organisation.id,agent_with_config.tools)
    except Exception as e:
        raise HTTPException(status_code=404,detail=str(e))

    if agent_with_config.schedule is not None:
        raise HTTPException(status_code=400,detail="Cannot schedule an existing agent")
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

    start_step = AgentWorkflow.fetch_trigger_step_id(db.session, db_agent.agent_workflow_id)
    iteration_step_id = IterationWorkflow.fetch_trigger_step_id(db.session,
                                                                start_step.action_reference_id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1
    execution = AgentExecution(status='CREATED', last_execution_time=datetime.now(), agent_id=db_agent.id,
                               name="New Run", current_agent_step_id=start_step.id, iteration_workflow_step_id=iteration_step_id)
    agent_execution_configs = {
        "goal": agent_with_config.goal,
        "instruction": agent_with_config.instruction,
        "tools":agent_with_config.tools,
        "constraints": agent_with_config.constraints,
        "iteration_interval": agent_with_config.iteration_interval,
        "model": agent_with_config.model,
        "max_iterations": agent_with_config.max_iterations,
        "agent_workflow": agent_with_config.agent_workflow,
    }
    agent_configurations = [
        AgentConfiguration(agent_id=db_agent.id, key=key, value=str(value))
        for key, value in agent_execution_configs.items()
    ]
    db.session.add_all(agent_configurations)
    db.session.add(execution)
    db.session.commit()
    db.session.flush()
    AgentExecutionConfiguration.add_or_update_agent_execution_config(session=db.session, execution=execution,
                                                                     agent_execution_configs=agent_execution_configs)
    db.session.commit()

    return {
        "agent_id":db_agent.id
    }


@router.post("/{agent_id}/run-status")
def get_agent_runs(agent_id:int,filter_config:RunFilterConfigIn,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):
    agent= Agent.get_active_agent_by_id(db.session, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    project=Project.find_by_id(db.session, agent.project_id)
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_execution_arr=[]
    if filter_config.run_status_filter is not None:
        filter_config.run_status_filter=filter_config.run_status_filter.upper()

    db_execution_arr=AgentExecution.get_all_executions_by_filter_config(db.session, agent.id, filter_config)
    
    response_arr=[]
    for ind_execution in db_execution_arr:
        response_arr.append({"run_id":ind_execution.id, "status":ind_execution.status})

    return response_arr


@router.post("/{agent_id}/pause",status_code=200)
def pause_agent_runs(agent_id:int,execution_state_change_input:ExecutionStateChangeConfigIn,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):
    agent= Agent.get_active_agent_by_id(db.session, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    project=Project.find_by_id(db.session, agent.project_id)
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    #Checking if the run_ids whose output files are requested belong to the organisation 
    if execution_state_change_input.run_ids is not None:
        try:
            AgentExecution.validate_run_ids(db.session,execution_state_change_input.run_ids,organisation.id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="One or more run_ids not found")
    
    db_execution_arr=AgentExecution.get_all_executions_by_status_and_agent_id(db.session, agent.id, execution_state_change_input, "RUNNING")
    for ind_execution in db_execution_arr:
        ind_execution.status="PAUSED"
    db.session.commit()
    db.session.flush()
    return {
        "result":"success"
    }

@router.post("/{agent_id}/resume",status_code=200)
def resume_agent_runs(agent_id:int,execution_state_change_input:ExecutionStateChangeConfigIn,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):
    agent= Agent.get_active_agent_by_id(db.session, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    project=Project.find_by_id(db.session, agent.project_id)
    if project.organisation_id!=organisation.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if execution_state_change_input.run_ids is not None:
        try:
            AgentExecution.validate_run_ids(db.session,execution_state_change_input.run_ids,organisation.id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="One or more run_ids not found")
    
    db_execution_arr=AgentExecution.get_all_executions_by_status_and_agent_id(db.session, agent.id, execution_state_change_input, "PAUSED")
    for ind_execution in db_execution_arr:
        ind_execution.status="RUNNING"
        execute_agent.delay(ind_execution.id, datetime.now())
        
    db.session.commit()
    db.session.flush()

    return {
        "result":"success"
    }

@router.post("/resources/output",status_code=201)
def get_run_resources(run_id_config:RunIDConfig,api_key: str = Security(validate_api_key),organisation:Organisation = Depends(get_organisation_from_api_key)):
    if get_config('STORAGE_TYPE') != "S3":
        raise HTTPException(status_code=400,detail="This endpoint only works when S3 is configured")
    run_ids_arr=run_id_config.run_ids
    if len(run_ids_arr)==0:  
        raise HTTPException(status_code=404,
                            detail=f"No execution_id found")
    #Checking if the run_ids whose output files are requested belong to the organisation 
    try:
        AgentExecution.validate_run_ids(db.session,run_ids_arr,organisation.id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="One or more run_ids not found")
    
    db_resources_arr=Resource.find_by_run_ids(db.session, run_ids_arr)

    try:
        response_obj=S3Helper().get_download_url_of_resources(db_resources_arr)
    except:
        raise HTTPException(status_code=401,detail="Invalid S3 credentials")
    return response_obj

