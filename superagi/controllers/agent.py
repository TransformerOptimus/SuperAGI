from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent import Agent
from superagi.models.agent_template import AgentTemplate
from superagi.models.agent_template_config import AgentTemplateConfig
from superagi.models.project import Project
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.types.agent_with_config import AgentWithConfig
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.tool import Tool
from jsonmerge import merge
from superagi.worker import execute_agent
from datetime import datetime
import json
from sqlalchemy import func
from superagi.helper.auth import check_auth, get_user_organisation

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Agent), status_code=201)
def create_agent(agent: sqlalchemy_to_pydantic(Agent, exclude=["id"]),
                 Authorize: AuthJWT = Depends(check_auth)):
    """Create agent new agent"""

    project = db.session.query(Project).get(agent.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_agent = Agent(name=agent.name, description=agent.description, project_id=agent.project_id)
    db.session.add(db_agent)
    db.session.commit()
    return db_agent


@router.get("/get/{agent_id}", response_model=sqlalchemy_to_pydantic(Agent))
def get_agent(agent_id: int,
              Authorize: AuthJWT = Depends(check_auth)):
    """Get particular agent by agent_id"""

    db_agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")
    return db_agent


@router.put("/update/{agent_id}", response_model=sqlalchemy_to_pydantic(Agent))
def update_agent(agent_id: int, agent: sqlalchemy_to_pydantic(Agent, exclude=["id"]),
                 Authorize: AuthJWT = Depends(check_auth)):
    """Update agent by agent_id"""

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
def create_agent_with_config(agent_with_config: AgentWithConfig,
                             Authorize: AuthJWT = Depends(check_auth)):
    """Create new agent with configurations"""

    # Checking for project
    project = db.session.query(Project).get(agent_with_config.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for tool_id in agent_with_config.tools:
        tool = db.session.query(Tool).get(tool_id)
        if tool is None:
            # Tool does not exist, throw 404 or handle as desired
            raise HTTPException(status_code=404, detail=f"Tool with ID {tool_id} does not exist. 404 Not Found.")
    db_agent = Agent.create_agent_with_config(db, agent_with_config)
    start_step_id = AgentWorkflow.fetch_trigger_step_id(db.session, db_agent.agent_workflow_id)
    # Creating an execution with CREATED status
    execution = AgentExecution(status='RUNNING', last_execution_time=datetime.now(), agent_id=db_agent.id,
                               name="New Run", current_step_id=start_step_id)

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
def get_agents_by_project_id(project_id: int,
                             Authorize: AuthJWT = Depends(check_auth)):
    """Get all agents by project_id"""

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
        new_agent = {
            **agent_dict,
            'status': isRunning
        }
        new_agents.append(new_agent)
    return new_agents


@router.get("/get/details/{agent_id}")
def get_agent_configuration(agent_id: int,
                            Authorize: AuthJWT = Depends(check_auth)):
    """Get agent using agent_id with all its configuration"""

    # Define the agent_config keys to fetch
    keys_to_fetch = AgentTemplate.main_keys()
    agent = db.session.query(Agent).filter(agent_id == Agent.id).first()

    if not agent:
        raise HTTPException(status_code=400, detail="Agent not found")

    # Query the AgentConfiguration table for the specified keys
    results = db.session.query(AgentConfiguration).filter(AgentConfiguration.key.in_(keys_to_fetch),
                                                          AgentConfiguration.agent_id == agent_id).all()
    total_calls = db.session.query(func.sum(AgentExecution.num_of_calls)).filter(
        AgentExecution.agent_id == agent_id).scalar()
    total_tokens = db.session.query(func.sum(AgentExecution.num_of_tokens)).filter(
        AgentExecution.agent_id == agent_id).scalar()

    # Construct the JSON response
    response = {result.key: result.value for result in results}
    response = merge(response, {"name": agent.name, "description": agent.description,
                                "goal": eval(response["goal"]),
                                "calls": total_calls,
                                "tokens": total_tokens,
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