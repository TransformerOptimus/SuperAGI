from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic


router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentConfiguration),status_code=201)
def create_agent(agent_config: sqlalchemy_to_pydantic(AgentConfiguration, exclude=["id"]),Authorize: AuthJWT = Depends()):

    agent = db.session.query(Agent).get(agent_config.agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_agent_config = AgentConfiguration(agent_id=agent_config.agent_id,key=agent_config.key,value=agent_config.value)
    db.session.add(db_agent_config)
    db.session.commit()
    return db_agent_config


@router.get("/get/{agent_config_id}", response_model=sqlalchemy_to_pydantic(AgentConfiguration))
def get_agent(agent_config_id: int,Authorize: AuthJWT = Depends()):
    db_agent_condfig = db.session.query(AgentConfiguration).filter(AgentConfiguration.id == agent_config_id).first()
    if not db_agent_condfig:
        raise HTTPException(status_code=404, detail="Agent Configuration not found")
    return db_agent_condfig



@router.put("/update/{agent_config_id}", response_model=sqlalchemy_to_pydantic(AgentConfiguration))
def update_agent(agent_config_id: int, agent_config: sqlalchemy_to_pydantic(AgentConfiguration,exclude=["id"])):
    db_agent_config = db.session.query(AgentConfiguration).filter(AgentConfiguration.id == agent_config_id).first()
    if not db_agent_config:
        raise HTTPException(status_code=404, detail="Agent Configuration not found")

    if agent_config.agent_id:
        agent = db.session.query(Agent).get(agent_config.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        db_agent_config.agent_id = agent.id
    db_agent_config.key = agent_config.key
    db_agent_config.value = agent_config.value

    db.session.commit()
    return db_agent_config