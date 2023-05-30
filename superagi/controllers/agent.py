from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent import Agent
from superagi.models.agent import Project
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.models.types.agent_with_config import AgentWithConfig
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.tool import Tool
from jsonmerge import merge
from superagi.worker import execute_agent
from datetime import datetime
import json

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Agent), status_code=201)
def create_agent(agent: sqlalchemy_to_pydantic(Agent, exclude=["id"]), Authorize: AuthJWT = Depends()):
    project = db.session.query(Project).get(agent.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_agent = Agent(name=agent.name, description=agent.description, project_id=agent.project_id)
    db.session.add(db_agent)
    db.session.commit()
    print(db_agent)
    return db_agent


@router.get("/get/{agent_id}", response_model=sqlalchemy_to_pydantic(Agent))
def get_agent(agent_id: int, Authorize: AuthJWT = Depends()):
    db_agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")
    return db_agent


@router.put("/update/{agent_id}", response_model=sqlalchemy_to_pydantic(Agent))
def update_agent(agent_id: int, agent: sqlalchemy_to_pydantic(Agent, exclude=["id"])):
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


@router.post("/create", status_code=201)
def create_agent_with_config(agent_with_config: AgentWithConfig):
    # Checking for project
    project = db.session.query(Project).get(agent_with_config.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for tool_id in agent_with_config.tools:
        tool = db.session.query(Tool).get(tool_id)
        if tool is None:
            # Tool does not exist, throw 404 or handle as desired
            raise HTTPException(status_code=404, detail=f"Tool with ID {tool_id} does not exist. 404 Not Found.")

    db_agent = Agent(name=agent_with_config.name, description=agent_with_config.description,
                     project_id=agent_with_config.project_id)
    db.session.add(db_agent)
    db.session.flush()  # Flush pending changes to generate the agent's ID
    db.session.commit()

    # Create Agent Configuration
    agent_config_values = {
        "goal": agent_with_config.goal,
        "agent_type": agent_with_config.agent_type,
        "constraints": agent_with_config.constraints,
        "tools": agent_with_config.tools,
        "exit": agent_with_config.exit,
        "iteration_interval": agent_with_config.iteration_interval,
        "model": agent_with_config.model,
        "permission_type": agent_with_config.permission_type,
        "LTM_DB": agent_with_config.LTM_DB,
        "memory_window": agent_with_config.memory_window
    }

    agent_configurations = [
        AgentConfiguration(agent_id=db_agent.id, key=key, value=str(value))
        for key, value in agent_config_values.items()
    ]
    db.session.add_all(agent_configurations)

    # Creating an execution with CREATED status
    execution = AgentExecution(status='RUNNING', last_execution_time=datetime.now(), agent_id=db_agent.id,
                               name="New Run")
    db.session.add(execution)
    db.session.commit()
    execute_agent.delay(execution.id, datetime.now())


    return {
        "id": db_agent.id,
        "execution_id": execution.id,
        "name": db_agent.name,
        "contentType": "Agents"
    }


@router.get("/get/project/{project_id}")
def get_agents_by_project_id(project_id: int):
    # Checking for project
    project = db.session.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    agents = db.session.query(Agent).filter(Agent.project_id == project_id).all()

    new_agents = []
    for agent in agents:
        agent_dict = vars(agent)
        agent_id = agent.id

        # Query the AgentExecution table using the agent ID
        executions = db.session.query(AgentExecution).filter_by(agent_id=agent_id).all()
        isRunning = False
        for execution in executions:
            if execution.status == "RUNNING":
                isRunning = True
                break
        # Add the execution status to the agent dictionary
        # agent['status'] = execution.status if execution else None
        new_agent = {
            **agent_dict,
            'status': isRunning
        }
        new_agents.append(new_agent)
    return new_agents


@router.get("/get/details/{agent_id}")
def get_agent_configuration(agent_id: int):
    # Define the keys to fetch
    keys_to_fetch = ["goal", "agent_type", "constraints", "tools", "exit", "iteration_interval", "model",
                     "permission_type", "LTM_DB", "memory_window"]

    agent = db.session.query(Agent).filter(agent_id == Agent.id).first()

    if not agent:
        raise HTTPException(status_code=400, detail="Agent not found")

    # Query the AgentConfiguration table for the specified keys
    results = db.session.query(AgentConfiguration).filter(AgentConfiguration.key.in_(keys_to_fetch),
                                                          AgentConfiguration.agent_id == agent_id).all()

    # Construct the JSON response
    response = {result.key: result.value for result in results}
    response = merge(response, {"name": agent.name, "description": agent.description,
                                "goal": eval(response["goal"]),
                                "constraints": eval(response["constraints"]),
                                "tools": [int(x) for x in json.loads(response["tools"])]})
    tools = db.session.query(Tool).filter(Tool.id.in_(response["tools"])).all()
    # print(tools)
    response["tools"] = tools
    # executions = db.session.query(AgentExecution).filter(AgentExecution.agent_id == agent_id).all()
    # response["executions"] = executions

    # Close the session
    db.session.close()

    return response
