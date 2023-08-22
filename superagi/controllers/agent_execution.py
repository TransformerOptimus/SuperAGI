from datetime import datetime
from typing import Optional, Union, List

from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from pydantic.fields import List
from superagi.controllers.types.agent_execution_config import AgentRunIn

from superagi.helper.time_helper import get_time_difference
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.agent_schedule import AgentSchedule
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.worker import execute_agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent import Agent
from fastapi import APIRouter
from sqlalchemy import desc
from superagi.helper.auth import check_auth
from superagi.controllers.types.agent_schedule import AgentScheduleInput
from superagi.apm.event_handler import EventHandler
from superagi.controllers.tool import ToolOut
from superagi.models.agent_config import AgentConfiguration

router = APIRouter()


class AgentExecutionOut(BaseModel):
    id: int
    status: str
    name: str
    agent_id: int
    last_execution_time: datetime
    num_of_calls: int
    num_of_tokens: int
    current_agent_step_id: int
    permission_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AgentExecutionIn(BaseModel):
    status: Optional[str]
    name: Optional[str]
    agent_id: Optional[int]
    last_execution_time: Optional[datetime]
    num_of_calls: Optional[int]
    num_of_tokens: Optional[int]
    current_agent_step_id: Optional[int]
    permission_id: Optional[int]
    goal: Optional[List[str]]
    instruction: Optional[List[str]]

    class config:
        orm_mode = True


# CRUD Operations
@router.post("/add", response_model=AgentExecutionOut, status_code=201)
def create_agent_execution(agent_execution: AgentExecutionIn,
                           Authorize: AuthJWT = Depends(check_auth)):
    """
    Create a new agent execution/run.

    Args:
        agent_execution (AgentExecution): The agent execution data.

    Returns:
        AgentExecution: The created agent execution.

    Raises:
        HTTPException (Status Code=404): If the agent is not found.
    """

    agent = db.session.query(Agent).filter(Agent.id == agent_execution.agent_id, Agent.is_deleted == False).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    start_step = AgentWorkflow.fetch_trigger_step_id(db.session, agent.agent_workflow_id)

    iteration_step_id = IterationWorkflow.fetch_trigger_step_id(db.session,
                                                                start_step.action_reference_id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1

    db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                        agent_id=agent_execution.agent_id, name=agent_execution.name, num_of_calls=0,
                                        num_of_tokens=0,
                                        current_agent_step_id=start_step.id,
                                        iteration_workflow_step_id=iteration_step_id)
    
    agent_execution_configs = {
        "goal": agent_execution.goal,
        "instruction": agent_execution.instruction
    }

    agent_configs = db.session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_execution.agent_id).all()
    keys_to_exclude = ["goal", "instruction"]
    for agent_config in agent_configs:
        if agent_config.key not in keys_to_exclude:
            if agent_config.key == "toolkits":
                if agent_config.value:
                    toolkits = [int(item) for item in agent_config.value.strip('{}').split(',') if item.strip() and item != '[]']
                    agent_execution_configs[agent_config.key] = toolkits
                else:
                    agent_execution_configs[agent_config.key] = []
            elif agent_config.key == "constraints":
                if agent_config.value:
                    agent_execution_configs[agent_config.key] = agent_config.value
                else:
                    agent_execution_configs[agent_config.key] = []
            else:
                agent_execution_configs[agent_config.key] = agent_config.value

    db.session.add(db_agent_execution)
    db.session.commit()
    db.session.flush()
    AgentExecutionConfiguration.add_or_update_agent_execution_config(session=db.session, execution=db_agent_execution,
                                                                     agent_execution_configs=agent_execution_configs)

    organisation = agent.get_agent_organisation(db.session)
    EventHandler(session=db.session).create_event('run_created', {'agent_execution_id': db_agent_execution.id,'agent_execution_name':db_agent_execution.name},
                                 agent_execution.agent_id, organisation.id if organisation else 0)

    if db_agent_execution.status == "RUNNING":
      execute_agent.delay(db_agent_execution.id, datetime.now())

    return db_agent_execution

@router.post("/add_run", status_code = 201)
def create_agent_run(agent_execution: AgentRunIn, Authorize: AuthJWT = Depends(check_auth)):

    """
    Create a new agent run with all the information(goals, instructions, model, etc).

    Args:
        agent_execution (AgentExecution): The agent execution data.

    Returns:
        AgentExecution: The created agent execution.

    Raises:
        HTTPException (Status Code=404): If the agent is not found.
    """
    agent = db.session.query(Agent).filter(Agent.id == agent_execution.agent_id, Agent.is_deleted == False).first()
    if not agent:
        raise HTTPException(status_code = 404, detail = "Agent not found")
    
    #Update the agent configurations table with the data of the latest agent execution
    AgentConfiguration.update_agent_configurations_table(session=db.session, agent_id=agent_execution.agent_id, updated_details=agent_execution)
    
    start_step = AgentWorkflow.fetch_trigger_step_id(db.session, agent.agent_workflow_id)

    iteration_step_id = IterationWorkflow.fetch_trigger_step_id(db.session,
                                                                start_step.action_reference_id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1

    db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                        agent_id=agent_execution.agent_id, name=agent_execution.name, num_of_calls=0,
                                        num_of_tokens=0,
                                        current_agent_step_id=start_step.id,
                                        iteration_workflow_step_id=iteration_step_id)
    agent_execution_configs = {
        "goal": agent_execution.goal,
        "instruction": agent_execution.instruction,
        "constraints": agent_execution.constraints,
        "toolkits": agent_execution.toolkits,
        "exit": agent_execution.exit,
        "tools": agent_execution.tools,
        "iteration_interval": agent_execution.iteration_interval,
        "model": agent_execution.model,
        "permission_type": agent_execution.permission_type,
        "LTM_DB": agent_execution.LTM_DB,
        "max_iterations": agent_execution.max_iterations,
        "user_timezone": agent_execution.user_timezone,
        "knowledge": agent_execution.knowledge
    }
    
    db.session.add(db_agent_execution)
    db.session.commit()
    db.session.flush()
    
    AgentExecutionConfiguration.add_or_update_agent_execution_config(session = db.session, execution = db_agent_execution,
                                                                     agent_execution_configs = agent_execution_configs)

    organisation = agent.get_agent_organisation(db.session)
    EventHandler(session=db.session).create_event('run_created', {'agent_execution_id': db_agent_execution.id,'agent_execution_name':db_agent_execution.name},
                                 agent_execution.agent_id, organisation.id if organisation else 0)

    if db_agent_execution.status == "RUNNING":
      execute_agent.delay(db_agent_execution.id, datetime.now())

    return db_agent_execution


@router.post("/schedule", status_code=201)
def schedule_existing_agent(agent_schedule: AgentScheduleInput,
                            Authorize: AuthJWT = Depends(check_auth)):

    """
    Schedules an already existing agent.

    Args:
        agent_schedule (AgentScheduleInput): Data for creating a scheduling for an existing agent.
            agent_id (Integer): The ID of the agent being scheduled.
            start_time (DateTime): The date and time from which the agent is scheduled.
            recurrence_interval (String): Stores "none" if not recurring, 
            or a time interval like '2 Weeks', '1 Month', '2 Minutes' based on input.
            expiry_date (DateTime): The date and time when the agent is scheduled to stop runs.
            expiry_runs (Integer): The number of runs before the agent expires.

    Returns:
        Schedule ID: Unique Schedule ID of the Agent.

    Raises:
        HTTPException (Status Code=500): If the agent fails to get scheduled.
    """

    # Check if the agent is already scheduled
    scheduled_agent = db.session.query(AgentSchedule).filter(AgentSchedule.agent_id == agent_schedule.agent_id,
                                                             AgentSchedule.status == "SCHEDULED").first()

    if scheduled_agent:
        # Update the old record with new data
        scheduled_agent.start_time = agent_schedule.start_time
        scheduled_agent.next_scheduled_time = agent_schedule.start_time
        scheduled_agent.recurrence_interval = agent_schedule.recurrence_interval
        scheduled_agent.expiry_date = agent_schedule.expiry_date
        scheduled_agent.expiry_runs = agent_schedule.expiry_runs

        db.session.commit()
    else:                      
        # Schedule the agent
        scheduled_agent = AgentSchedule(
            agent_id=agent_schedule.agent_id,
            start_time=agent_schedule.start_time,
            next_scheduled_time=agent_schedule.start_time,
            recurrence_interval=agent_schedule.recurrence_interval,
            expiry_date=agent_schedule.expiry_date,
            expiry_runs=agent_schedule.expiry_runs,
            current_runs=0,
            status="SCHEDULED"
        )

    db.session.add(scheduled_agent)
    db.session.commit()

    schedule_id = scheduled_agent.id

    if schedule_id is None:
        raise HTTPException(status_code=500, detail="Failed to schedule agent")
        
    return {
        "schedule_id": schedule_id
    }


@router.get("/get/{agent_execution_id}", response_model=AgentExecutionOut)
def get_agent_execution(agent_execution_id: int,
                        Authorize: AuthJWT = Depends(check_auth)):
    """
    Get an agent execution by agent_execution_id.

    Args:
        agent_execution_id (int): The ID of the agent execution.

    Returns:
        AgentExecution: The requested agent execution.

    Raises:
        HTTPException (Status Code=404): If the agent execution is not found.
    """

    if (
        db_agent_execution := db.session.query(AgentExecution)
        .filter(AgentExecution.id == agent_execution_id)
        .first()
    ):
        return db_agent_execution
    else:
        raise HTTPException(status_code=404, detail="Agent execution not found")


@router.put("/update/{agent_execution_id}", response_model=AgentExecutionOut)
def update_agent_execution(agent_execution_id: int,
                           agent_execution: AgentExecutionIn,
                           Authorize: AuthJWT = Depends(check_auth)):
    """Update details of particular agent_execution by agent_execution_id"""

    db_agent_execution = db.session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    if agent_execution.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Invalid Request")

    if not db_agent_execution:
        raise HTTPException(status_code=404, detail="Agent Execution not found")

    if agent_execution.agent_id:
        if agent := db.session.query(Agent).get(agent_execution.agent_id):
            db_agent_execution.agent_id = agent.id
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    if agent_execution.status not in [
        "CREATED",
        "RUNNING",
        "PAUSED",
        "COMPLETED",
        "TERMINATED",
    ]:
        raise HTTPException(status_code=400, detail="Invalid Request")
    db_agent_execution.status = agent_execution.status

    db_agent_execution.last_execution_time = datetime.now()
    db.session.commit()

    if db_agent_execution.status == "RUNNING":
        execute_agent.delay(db_agent_execution.id, datetime.now())

    return db_agent_execution


@router.get("/get/agents/status/{status}")
def agent_list_by_status(status: str,
                         Authorize: AuthJWT = Depends(check_auth)):
    """Get list of all agent_ids for a given status"""

    running_agent_ids = db.session.query(AgentExecution.agent_id).filter(
        AgentExecution.status == status.upper()).distinct().all()
    agent_ids = [agent_id for (agent_id) in running_agent_ids]
    return agent_ids


@router.get("/get/agent/{agent_id}")
def list_running_agents(agent_id: str,
                        Authorize: AuthJWT = Depends(check_auth)):
    """Get all running state agents"""

    executions = db.session.query(AgentExecution).filter(AgentExecution.agent_id == agent_id).order_by(
        desc(AgentExecution.status == 'RUNNING'), desc(AgentExecution.last_execution_time)).all()
    for execution in executions:
        execution.time_difference = get_time_difference(execution.last_execution_time,str(datetime.now()))
    return executions


@router.get("/get/latest/agent/project/{project_id}")
def get_agent_by_latest_execution(project_id: int,
                                  Authorize: AuthJWT = Depends(check_auth)):
    """Get latest executing agent details"""

    latest_execution = (
        db.session.query(AgentExecution)
        .join(Agent, AgentExecution.agent_id == Agent.id)
        .filter(Agent.project_id == project_id, Agent.is_deleted == False)
        .order_by(desc(AgentExecution.last_execution_time))
        .first()
    )
    isRunning = False
    if latest_execution.status == "RUNNING":
        isRunning = True
    agent = db.session.query(Agent).filter(Agent.id == latest_execution.agent_id).first()
    return {
        "agent_id": latest_execution.agent_id,
        "project_id": project_id,
        "created_at": agent.created_at,
        "description": agent.description,
        "updated_at": agent.updated_at,
        "name": agent.name,
        "id": agent.id,
        "status": isRunning,
        "contentType": "Agents"
    }