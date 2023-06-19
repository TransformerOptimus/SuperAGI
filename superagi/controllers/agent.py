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
    """
        Creates a new Agent

        Args:
            agent (Agent): An object representing the Agent to be created.
                Contains the following attributes:
                - name (str): Name of the Agent
                - project_id (int): Identifier of the associated project
                - description (str): Description of the Agent
                - agent_workflow_id (int): Identifier of the Agent Workflow in use

        Returns:
            Agent: An object of Agent representing the created Agent.

        Raises:
            HTTPException (Status Code=404): If the associated project is not found.
    """

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
    """
        Get an Agent by ID

        Args:
            agent_id (int): Identifier of the Agent to retrieve

        Returns:
            Agent: An object of Agent representing the retrieved Agent.

        Raises:
            HTTPException (Status Code=404): If the Agent is not found.
    """

    db_agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")
    return db_agent


@router.put("/update/{agent_id}", response_model=sqlalchemy_to_pydantic(Agent))
def update_agent(agent_id: int, agent: sqlalchemy_to_pydantic(Agent, exclude=["id"]),
                 Authorize: AuthJWT = Depends(check_auth)):
    """
        Update an existing Agent

        Args:
            agent_id (int): Identifier of the Agent to update
            agent (Agent):  Updated Agent data
                Contains the following attributes:
                - name (str): Name of the Agent
                - project_id (int): Identifier of the associated project
                - description (str): Description of the Agent
                - agent_workflow_id (int): Identifier of the Agent Workflow in use

        Returns:
            Agent: An object of Agent representing the updated Agent.

        Raises:
            HTTPException (Status Code=404): If the Agent or associated Project is not found.
    """

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
    """
    Create a new agent with configurations.

    Args:
        agent_with_config (AgentWithConfig): Data for creating a new agent with configurations.
            - name (str): Name of the agent.
            - project_id (int): Identifier of the associated project.
            - description (str): Description of the agent.
            - goal (List[str]): List of goals for the agent.
            - agent_type (str): Type of the agent.
            - constraints (List[str]): List of constraints for the agent.
            - tools (List[int]): List of tool identifiers associated with the agent.
            - exit (str): Exit condition for the agent.
            - iteration_interval (int): Interval between iterations for the agent.
            - model (str): Model information for the agent.
            - permission_type (str): Permission type for the agent.
            - LTM_DB (str): LTM database for the agent.
            - memory_window (int): Memory window size for the agent.
            - max_iterations (int): Maximum number of iterations for the agent.

    Returns:
        dict: Dictionary containing the created agent's ID, execution ID, name, and content type.

    Raises:
        HTTPException (status_code=404): If the associated project or any of the tools is not found.
    """

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
    """
    Get all agents by project ID.

    Args:
        project_id (int): Identifier of the project.
        Authorize (AuthJWT, optional): Authorization dependency. Defaults to Depends(check_auth).

    Returns:
        list: List of agents associated with the project, including their status.

    Raises:
        HTTPException (status_code=404): If the project is not found.
    """

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
    """
    Get the agent configuration using the agent ID.

    Args:
        agent_id (int): Identifier of the agent.
        Authorize (AuthJWT, optional): Authorization dependency. Defaults to Depends(check_auth).

    Returns:
        dict: Agent configuration including its details.

    Raises:
        HTTPException (status_code=404): If the agent is not found.
    """

    # Define the agent_config keys to fetch
    keys_to_fetch = AgentTemplate.main_keys()
    agent = db.session.query(Agent).filter(agent_id == Agent.id).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

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
    # Query the AgentConfiguration table for the speci
                                "goal": eval(response["goal"]),
                                "instruction": eval(response.get("instruction", '[]')),
                                "calls": total_calls,
                                "tokens": total_tokens,
                                "constraints": eval(response.get("constraints")),
                                "tools": [int(x) for x in json.loads(response["tools"])]})
    tools = db.session.query(Tool).filter(Tool.id.in_(response["tools"])).all()
    response["tools"] = tools

    # Close the session
    db.session.close()

    return response
