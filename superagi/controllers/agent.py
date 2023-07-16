import json
from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from jsonmerge import merge
from pytz import timezone
from sqlalchemy import func
from superagi.worker import execute_agent
from superagi.helper.auth import check_auth
from superagi.models.agent import Agent
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_schedule import AgentSchedule
from superagi.models.agent_template import AgentTemplate
from superagi.models.project import Project
from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.agent_execution import AgentExecution
from superagi.models.tool import Tool
from superagi.controllers.types.agent_schedule import AgentScheduleInput
from superagi.controllers.types.agent_with_config import AgentConfigInput
from superagi.controllers.types.agent_with_config_schedule import AgentConfigSchedule
from jsonmerge import merge
from datetime import datetime
import json

from superagi.models.toolkit import Toolkit

from sqlalchemy import func
# from superagi.types.db import AgentOut, AgentIn
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.apm.event_handler import EventHandler

router = APIRouter()


class AgentOut(BaseModel):
    id: int
    name: str
    project_id: int
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AgentIn(BaseModel):
    name: str
    project_id: int
    description: str

    class Config:
        orm_mode = True


# CRUD Operations
@router.post("/add", response_model=AgentOut, status_code=201)
def create_agent(agent: AgentIn,
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


@router.get("/get/{agent_id}", response_model=AgentOut)
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


@router.put("/update/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: int, agent: AgentIn,
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
def create_agent_with_config(agent_with_config: AgentConfigInput,
                             Authorize: AuthJWT = Depends(check_auth)):
    """
    Create a new agent with configurations.

    Args:
        agent_with_config (AgentConfigInput): Data for creating a new agent with configurations.
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
            - max_iterations (int): Maximum number of iterations for the agent.
            - user_timezone (string): Timezone of the user

    Returns:
        dict: Dictionary containing the created agent's ID, execution ID, name, and content type.

    Raises:
        HTTPException (status_code=404): If the associated project or any of the tools is not found.
    """

    project = db.session.query(Project).get(agent_with_config.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    invalid_tools = Tool.get_invalid_tools(agent_with_config.tools, db.session)
    if len(invalid_tools) > 0:  # If the returned value is not True (then it is an invalid tool_id)
        raise HTTPException(status_code=404, detail=f"Tool with IDs {str(invalid_tools)} does not exist. 404 Not Found.")

    agent_toolkit_tools = Toolkit.fetch_tool_ids_from_toolkit(session=db.session,
                                                              toolkit_ids=agent_with_config.toolkits)
    agent_with_config.tools.extend(agent_toolkit_tools)
    db_agent = Agent.create_agent_with_config(db, agent_with_config)

    start_step_id = AgentWorkflow.fetch_trigger_step_id(db.session, db_agent.agent_workflow_id)
    # Creating an execution with RUNNING status
    execution = AgentExecution(status='CREATED', last_execution_time=datetime.now(), agent_id=db_agent.id,
                               name="New Run", current_step_id=start_step_id)

    agent_execution_configs = {
        "goal": agent_with_config.goal,
        "instruction": agent_with_config.instruction
    }
    db.session.add(execution)
    db.session.commit()
    db.session.flush()
    AgentExecutionConfiguration.add_or_update_agent_execution_config(session=db.session, execution=execution,
                                                                     agent_execution_configs=agent_execution_configs)

    agent = db.session.query(Agent).filter(Agent.id == db_agent.id,).first()
    organisation = agent.get_agent_organisation(db.session)
    EventHandler(session=db.session).create_event('run_created', {'agent_execution_id': execution.id,'agent_execution_name':execution.name}, db_agent.id, organisation.id if organisation else 0),
    EventHandler(session=db.session).create_event('agent_created', {'agent_name': agent_with_config.name, 'model': agent_with_config.model}, db_agent.id, organisation.id if organisation else 0)

    # execute_agent.delay(execution.id, datetime.now())

    db.session.commit()

    return {
        "id": db_agent.id,
        "execution_id": execution.id,
        "name": db_agent.name,
        "contentType": "Agents"
    }

@router.post("/schedule", status_code=201)
def create_and_schedule_agent(agent_config_schedule: AgentConfigSchedule,
                              Authorize: AuthJWT = Depends(check_auth)):
    """
    Create a new agent with configurations and scheduling.

    Args:
        agent_with_config_schedule (AgentConfigSchedule): Data for creating a new agent with configurations and scheduling.

    Returns:
        dict: Dictionary containing the created agent's ID, name, content type and schedule ID of the agent.

    Raises:
        HTTPException (status_code=500): If the associated agent fails to get scheduled.
    """

    project = db.session.query(Project).get(agent_config_schedule.agent_config.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    agent_config = agent_config_schedule.agent_config
    invalid_tools = Tool.get_invalid_tools(agent_config.tools, db.session)
    if len(invalid_tools) > 0:  # If the returned value is not True (then it is an invalid tool_id)
        raise HTTPException(status_code=404, detail=f"Tool with IDs {str(invalid_tools)} does not exist. 404 Not Found.")

    agent_toolkit_tools = Toolkit.fetch_tool_ids_from_toolkit(session=db.session,
                                                              toolkit_ids=agent_config.toolkits)
    agent_config.tools.extend(agent_toolkit_tools)
    db_agent = Agent.create_agent_with_config(db, agent_config)

    # Update the agent_id of schedule before scheduling the agent
    agent_schedule = agent_config_schedule.schedule

    # Create a new agent schedule
    agent_schedule = AgentSchedule(
        agent_id=db_agent.id,
        start_time=agent_schedule.start_time,
        next_scheduled_time=agent_schedule.start_time,
        recurrence_interval=agent_schedule.recurrence_interval,
        expiry_date=agent_schedule.expiry_date,
        expiry_runs=agent_schedule.expiry_runs,
        current_runs=0,
        status="SCHEDULED"
    )

    agent_schedule.agent_id = db_agent.id
    db.session.add(agent_schedule)
    db.session.commit()

    if agent_schedule.id is None:
        raise HTTPException(status_code=500, detail="Failed to schedule agent")

    return {
        "id": db_agent.id,
        "name": db_agent.name,
        "contentType": "Agents",
        "schedule_id": agent_schedule.id
    }

@router.post("/stop/schedule", status_code=200)
def stop_schedule(agent_id: int, Authorize: AuthJWT = Depends(check_auth)):
    """
    Stopping the scheduling for a given agent.

    Args:
        agent_id (int): Identifier of the Agent
        Authorize (AuthJWT, optional): Authorization dependency. Defaults to Depends(check_auth).

    Raises:
        HTTPException (status_code=404): If the agent schedule is not found.
    """

    agent_to_delete = db.session.query(AgentSchedule).filter(AgentSchedule.agent_id == agent_id,
                                                              AgentSchedule.status == "SCHEDULED").first()
    if not agent_to_delete:
        raise HTTPException(status_code=404, detail="Schedule not found")
    agent_to_delete.status = "STOPPED"
    db.session.commit()


@router.put("/edit/schedule", status_code=200)
def edit_schedule(schedule: AgentScheduleInput,
                  Authorize: AuthJWT = Depends(check_auth)):
    """
    Edit the scheduling for a given agent.

    Args:
        agent_id (int): Identifier of the Agent
        schedule (AgentSchedule): New schedule data
        Authorize (AuthJWT, optional): Authorization dependency. Defaults to Depends(check_auth).

    Raises:
        HTTPException (status_code=404): If the agent schedule is not found.
    """

    agent_to_edit = db.session.query(AgentSchedule).filter(AgentSchedule.agent_id == schedule.agent_id,
                                                            AgentSchedule.status == "SCHEDULED").first()
    if not agent_to_edit:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Update agent schedule with new data
    agent_to_edit.start_time = schedule.start_time
    agent_to_edit.next_scheduled_time = schedule.start_time
    agent_to_edit.recurrence_interval = schedule.recurrence_interval
    agent_to_edit.expiry_date = schedule.expiry_date
    agent_to_edit.expiry_runs = schedule.expiry_runs

    db.session.commit()


@router.get("/get/schedule_data/{agent_id}")
def get_schedule_data(agent_id: int, Authorize: AuthJWT = Depends(check_auth)):
    """
    Get the scheduling data for a given agent.

    Args:
        agent_id (int): Identifier of the Agent

    Raises:
        HTTPException (status_code=404): If the agent schedule is not found.

    Returns:
        current_datetime (DateTime): Current Date and Time.
        recurrence_interval (String): Time interval for recurring schedule run.
        expiry_date (DateTime): The date and time when the agent is scheduled to stop runs.
        expiry_runs (Integer): The number of runs before the agent expires.
    """
    agent = db.session.query(AgentSchedule).filter(AgentSchedule.agent_id == agent_id,
                                                    AgentSchedule.status == "SCHEDULED").first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent Schedule not found")

    user_timezone = db.session.query(AgentConfiguration).filter(AgentConfiguration.key == "user_timezone",
                                                                AgentConfiguration.agent_id == agent_id).first()

    if user_timezone and user_timezone.value != "None":
        tzone = timezone(user_timezone.value)
    else:
        tzone = timezone('GMT')


    current_datetime = datetime.now(tzone).strftime("%d/%m/%Y %I:%M %p")

    response_data = {
        "current_datetime": current_datetime,
        "start_date": agent.start_time.astimezone(tzone).strftime("%d %b %Y"),
        "start_time": agent.start_time.astimezone(tzone).strftime("%I:%M %p"),
        "recurrence_interval": agent.recurrence_interval if agent.recurrence_interval else None,
        "expiry_date": agent.expiry_date.astimezone(tzone).strftime("%d/%m/%Y") if agent.expiry_date else None,
        "expiry_runs": agent.expiry_runs if agent.expiry_runs != -1 else None
    }

    return response_data


@router.get("/get/project/{project_id}")
def get_agents_by_project_id(project_id: int,
                             Authorize: AuthJWT = Depends(check_auth)):
    """
    Get all agents by project ID.

    Args:
        project_id (int): Identifier of the project.
        Authorize (AuthJWT, optional): Authorization dependency. Defaults to Depends(check_auth).

    Returns:
        list: List of agents associated with the project, including their status and scheduling information.

    Raises:
        HTTPException (status_code=404): If the project is not found.
    """

    # Checking for project
    project = db.session.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    agents = db.session.query(Agent).filter(Agent.project_id == project_id).all()

    new_agents, new_agents_sorted = [], []
    for agent in agents:
        agent_dict = vars(agent)
        agent_id = agent.id

        # Query the AgentExecution table using the agent ID
        executions = db.session.query(AgentExecution).filter_by(agent_id=agent_id).all()
        is_running = False
        for execution in executions:
            if execution.status == "RUNNING":
                is_running = True
                break
        # Check if the agent is scheduled
        is_scheduled = db.session.query(AgentSchedule).filter_by(agent_id=agent_id,
                                                                  status="SCHEDULED").first() is not None

        new_agent = {
            **agent_dict,
            'is_running': is_running,
            'is_scheduled': is_scheduled
        }
        new_agents.append(new_agent)
        new_agents_sorted = sorted(new_agents, key=lambda agent: agent['is_running'] == True, reverse=True)
    return new_agents_sorted


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
