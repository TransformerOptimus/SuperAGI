from datetime import datetime

from celery import Celery
from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from superagi.worker import execute_agent
from superagi.agent import super_agi
from superagi.config.config import get_config
from superagi.jobs.agent_executor import AgentExecutor
# import worker
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent import Agent
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import desc

# import superagi.worker

router = APIRouter()

# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentExecution), status_code=201)
def create_agent_execution(agent_execution: sqlalchemy_to_pydantic(AgentExecution, exclude=["id"]),
                           Authorize: AuthJWT = Depends()):
    agent = db.session.query(Agent).get(agent_execution.agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                        agent_id=agent_execution.agent_id,name=agent_execution.name)
    db.session.add(db_agent_execution)
    db.session.commit()
    if db_agent_execution.status == "RUNNING":
        execute_agent.delay(db_agent_execution.id, datetime.now())

    return db_agent_execution


@router.get("/get/{agent_execution_id}", response_model=sqlalchemy_to_pydantic(AgentExecution))
def get_agent_execution(agent_execution_id: int, Authorize: AuthJWT = Depends()):
    # Authorize.jwt_required()
    db_agent_execution = db.session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    if not db_agent_execution:
        raise HTTPException(status_code=404, detail="Agent execution not found")
    return db_agent_execution


@router.put("/update/{agent_execution_id}", response_model=sqlalchemy_to_pydantic(AgentExecution))
def update_agent_execution(agent_execution_id: int,
                           agent_execution: sqlalchemy_to_pydantic(AgentExecution, exclude=["id"])):
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
    if agent_execution.name != None:
        db_agent_execution.name = agent_execution.name
    db.session.commit()

    if db_agent_execution.status == "RUNNING":
        execute_agent.delay(db_agent_execution.id, datetime.now())

    return db_agent_execution


@router.get("/get/agents/status/{status}")
def list_running_agents(status: str):
    running_agent_ids = db.session.query(AgentExecution.agent_id).filter(
        AgentExecution.status == status.upper()).distinct().all()
    agent_ids = [agent_id for (agent_id) in running_agent_ids]
    return agent_ids


@router.get("/get/agent/{agent_id}")
def list_running_agents(agent_id: str):
    executions = db.session.query(AgentExecution).filter(AgentExecution.agent_id == agent_id).order_by(
        desc(AgentExecution.status == 'RUNNING'), desc(AgentExecution.last_execution_time)).all()
    return executions


@router.get("/get/latest/agent/project/{project_id}")
def get_agent_by_latest_execution(project_id:int):
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
