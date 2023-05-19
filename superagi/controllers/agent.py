from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent import Agent
from superagi.models.agent import Project
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic


router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Agent),status_code=201)
def create_agent(agent: sqlalchemy_to_pydantic(Agent, exclude=["id"]),Authorize: AuthJWT = Depends()):

    project = db.session.query(Project).get(agent.project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_agent = Agent(name=agent.name, description=agent.description,project_id=agent.project_id)
    db.session.add(db_agent)
    db.session.commit()
    return db_agent


@router.get("/get/{agent_id}", response_model=sqlalchemy_to_pydantic(Agent))
def get_agent(agent_id: int,Authorize: AuthJWT = Depends()):
    db_agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")
    return db_agent



@router.put("/update/{agent_id}", response_model=sqlalchemy_to_pydantic(Agent))
def update_agent(agent_id: int, agent: sqlalchemy_to_pydantic(Agent,exclude=["id"])):
    db_agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")

    if agent.project_id:
        project = db.session.query(Project).get(agent.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        db_agent.project_id = project.id
    db_agent.name = agent.name
    db_agent.description = agent.description

    db.session.commit()
    return db_agent
