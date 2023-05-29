from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent import Agent
from superagi.models.types.agent_config import AgentConfig
from superagi.models.agent_config import AgentConfiguration
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentConfiguration), status_code=201)
def create_agent(agent_config: sqlalchemy_to_pydantic(AgentConfiguration, exclude=["id"]),
                 Authorize: AuthJWT = Depends()):
    agent = db.session.query(Agent).get(agent_config.agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db_agent_config = AgentConfiguration(agent_id=agent_config.agent_id, key=agent_config.key, value=agent_config.value)
    db.session.add(db_agent_config)
    db.session.commit()
    return db_agent_config


@router.get("/get/{agent_config_id}", response_model=sqlalchemy_to_pydantic(AgentConfiguration))
def get_agent(agent_config_id: int, Authorize: AuthJWT = Depends()):
    db_agent_config = db.session.query(AgentConfiguration).filter(AgentConfiguration.id == agent_config_id).first()
    if not db_agent_config:
        raise HTTPException(status_code=404, detail="Agent Configuration not found")
    return db_agent_config


@router.put("/update", response_model=sqlalchemy_to_pydantic(AgentConfiguration))
def update_agent(agent_config: AgentConfig):
    db_agent_config = db.session.query(AgentConfiguration).filter(AgentConfiguration.key == agent_config.key,
                                                                  AgentConfiguration.agent_id == agent_config.agent_id).first()
    if not db_agent_config:
        raise HTTPException(status_code=404, detail="Agent Configuration not found")

    db_agent_config.key = agent_config.key
    if isinstance(agent_config.value, list):
        # Convert the list to a string using the str() function
        db_agent_config.value = str(agent_config.value)
    else:
        db_agent_config.value = agent_config.value
    db.session.commit()
    db.session.flush()
    return db_agent_config


@router.get("/get/agent/{agent_id}")
def get_agent_configurations(agent_id: int):
    agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="agent not found")

    agent_configurations = db.session.query(AgentConfiguration).filter_by(agent_id=agent_id).all()
    if not agent_configurations:
        raise HTTPException(status_code=404, detail="Agent configurations not found")

    parsed_response = {
        "agent_id": agent_id,
        "name": agent.name,
        "project_id": agent.project_id,
        "description": agent.description,
        "goal": [],
        "agent_type": None,
        "constraints": None,
        "tools": [],
        "exit": None,
        "iteration_interval": None,
        "model": None,
        "permission_type": None,
        "LTM_DB": None,
    }

    for item in agent_configurations:
        key = item.key
        value = item.value

        if key == "name":
            parsed_response["name"] = value
        elif key == "project_id":
            parsed_response["project_id"] = int(value)
        elif key == "description":
            parsed_response["description"] = value
        elif key == "goal":
            parsed_response["goal"] = eval(value)  # Using eval to parse the list of strings
        elif key == "agent_type":
            parsed_response["agent_type"] = value
        elif key == "constraints":
            parsed_response["constraints"] = eval(value)  # Using eval to parse the list of strings
        elif key == "tools":
            parsed_response["tools"] = eval(value)  # Using eval to parse the list of strings
        elif key == "exit":
            parsed_response["exit"] = value
        elif key == "iteration_interval":
            parsed_response["iteration_interval"] = int(value)
        elif key == "model":
            parsed_response["model"] = value
        elif key == "permission_type":
            parsed_response["permission_type"] = value
        elif key == "LTM_DB":
            parsed_response["LTM_DB"] = value

    return parsed_response
