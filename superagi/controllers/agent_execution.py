from datetime import datetime
from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from superagi.helper.time_helper import get_time_difference
from superagi.models.agent_workflow import AgentWorkflow

from superagi.models.agent_schedule import AgentSchedule
from superagi.worker import execute_agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent import Agent
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import desc
from superagi.helper.auth import check_auth

from superagi.controllers.types.agent_schedule import AgentScheduler

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentExecution), status_code=201)
def create_agent_execution(agent_execution: sqlalchemy_to_pydantic(AgentExecution, exclude=["id"]),
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

    agent = db.session.query(Agent).get(agent_execution.agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    start_step_id = AgentWorkflow.fetch_trigger_step_id(db.session, agent.agent_workflow_id)
    db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                        agent_id=agent_execution.agent_id, name=agent_execution.name, num_of_calls=0,
                                        num_of_tokens=0,
                                        current_step_id=start_step_id)
    db.session.add(db_agent_execution)
    db.session.commit()
    if db_agent_execution.status == "RUNNING":
        execute_agent.delay(db_agent_execution.id, datetime.now())

    return db_agent_execution

@router.post("/schedule", status_code=201)
def schedule_existing_agent(agent_schedule: AgentScheduler,
                            Authorize: AuthJWT = Depends(check_auth)):
    
    """
    Schedules an already existing agent.

    Args:
        agent_schedule (AgentScheduler): Data for creating a scheduling for an existing agent.
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
    scheduled_agent = db.session.query(AgentSchedule).filter(AgentSchedule.agent_id == agent_schedule.agent_id, AgentSchedule.status=="RUNNING").first()

    if scheduled_agent:
        # Update the old record with new data
        scheduled_agent.start_time = agent_schedule.start_time
        scheduled_agent.next_scheduled_time =  agent_schedule.start_time
        scheduled_agent.recurrence_interval = agent_schedule.recurrence_interval
        scheduled_agent.expiry_date = agent_schedule.expiry_date
        scheduled_agent.expiry_runs = agent_schedule.expiry_runs

        schedule_id = scheduled_agent.id

        db.session.commit()
    else:                      
        # Schedule the agent
        schedule_id = AgentSchedule.schedule_agent(db.session, agent_schedule)

    if schedule_id is None:
        raise HTTPException(status_code=500, detail="Failed to schedule agent")
        
    return {
        "schedule_id": schedule_id
    }

@router.get("/get/{agent_execution_id}", response_model=sqlalchemy_to_pydantic(AgentExecution))
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

    db_agent_execution = db.session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    if not db_agent_execution:
        raise HTTPException(status_code=404, detail="Agent execution not found")
    return db_agent_execution


@router.put("/update/{agent_execution_id}", response_model=sqlalchemy_to_pydantic(AgentExecution))
def update_agent_execution(agent_execution_id: int,
                        agent_execution: sqlalchemy_to_pydantic(AgentExecution, exclude=["id"]),
                        Authorize: AuthJWT = Depends(check_auth)):
    """Update details of particular agent_execution by agent_execution_id"""

    db_agent_execution = db.session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    if agent_execution == "COMPLETED":
        raise HTTPException(status_code=400, detail="Invalid Request")

    if not db_agent_execution:
        raise HTTPException(status_code=404, detail="Agent Execution not found")

    if agent_execution.agent_id:
        agent = db.session.query(Agent).get(agent_execution.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        db_agent_execution.agent_id = agent.id
    if agent_execution.status != "CREATED" and agent_execution.status != "RUNNING" and agent_execution.status != "PAUSED" and agent_execution.status != "COMPLETED" and agent_execution.status != "TERMINATED":
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
        .filter(Agent.project_id == project_id)
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
