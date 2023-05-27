from datetime import datetime
from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent import Agent
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from celery_app import test_fucntion
from sqlalchemy import desc


router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentExecution),status_code=201)
def create_agent_execution(agent_execution: sqlalchemy_to_pydantic(AgentExecution, exclude=["id"]),Authorize: AuthJWT = Depends()):
    agent = db.session.query(Agent).get(agent_execution.agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_agent_execution = AgentExecution(status="CREATED",last_execution_time=datetime.now(),agent_id=agent_execution.agent_id,name=agent_execution.name)
    db.session.add(db_agent_execution)
    db.session.commit()
    return db_agent_execution


@router.get("/get/{agent_execution_id}", response_model=sqlalchemy_to_pydantic(AgentExecution))
def get_agent_execution(agent_execution_id: int,Authorize: AuthJWT = Depends()):
    # Authorize.jwt_required()
    db_agent_execution = db.session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    if not db_agent_execution:
        raise HTTPException(status_code=404, detail="Agent execution not found")
    return db_agent_execution


@router.put("/update/{agent_execution_id}", response_model=sqlalchemy_to_pydantic(AgentExecution))
def update_agent_execution(agent_execution_id: int, agent_execution: sqlalchemy_to_pydantic(AgentExecution,exclude=["id"])):
    db_agent_execution = db.session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    if agent_execution=="COMPLETED":
        raise HTTPException(status_code=400, detail="Invalid Request")

    if not db_agent_execution:
        raise HTTPException(status_code=404, detail="Agent Execution not found")

    if agent_execution.agent_id:
        agent = db.session.query(Agent).get(agent_execution.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        db_agent_execution.agent_id = agent.id
    if agent_execution.status != "CREATED" and agent_execution.status != "RUNNING" and agent_execution.status != "PAUSED" and agent_execution.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Invalid Request")
    db_agent_execution.status = agent_execution.status
    db_agent_execution.last_execution_time = datetime.now()
    db_agent_execution.name = agent_execution.name

    db.session.commit()

    if db_agent_execution.status == "RUNNING":
        print("DB EXEC : ")
        print(db_agent_execution)
        print("JSON:")
        print(db_agent_execution.to_json())
        test_fucntion.delay(db_agent_execution.to_json())
        # test_fucntion.delay(db_agent_execution)


    return db_agent_execution


@router.get("/get/agents/status/{status}")
def list_running_agents(status:str):
    running_agent_ids = db.session.query(AgentExecution.agent_id).filter(AgentExecution.status == status.upper()).distinct().all()
    agent_ids = [agent_id for (agent_id) in running_agent_ids]
    return agent_ids

@router.get("/get/agent/{agent_id}")
def list_running_agents(agent_id:str):

    # print("")
    # running_agent_ids = db.session.query(AgentExecution.agent_id).filter(AgentExecution.status == status.upper()).distinct().all()
    executions = db.session.query(AgentExecution).filter(AgentExecution.agent_id == agent_id).order_by(desc(AgentExecution.status == 'RUNNING'), desc(AgentExecution.last_execution_time)).all()
    return executions