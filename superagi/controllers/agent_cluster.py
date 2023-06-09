from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from superagi.helper.auth import check_auth
from superagi.models.agent_cluster import AgentCluster
from superagi.models.project import Project
from fastapi_sqlalchemy import db
router = APIRouter()


@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentCluster), status_code=201)
def create_agent(agent_cluster: sqlalchemy_to_pydantic(AgentCluster, exclude=["id"]),
                 Authorize: AuthJWT = Depends(check_auth)):
    """Create agent new agent"""

    project = db.session.query(Project).get(agent_cluster.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_agent = AgentCluster(name=agent_cluster.name, description=agent_cluster.description, project_id=agent_cluster.project_id)
    db.session.add(db_agent)
    db.session.commit()
    return db_agent


@router.get("/get/{agent_cluster_id}", response_model=sqlalchemy_to_pydantic(AgentCluster))
def get_agent(agent_cluster_id: int,
              Authorize: AuthJWT = Depends(check_auth)):
    """Get particular agent by agent_id"""

    db_agent = db.session.query(AgentCluster).filter(AgentCluster.id == agent_cluster_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")
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

    db_agent = Agent(name=agent_with_config.name, description=agent_with_config.description,
                     project_id=agent_with_config.project_id)
    db.session.add(db_agent)
    db.session.flush()  # Flush pending changes to generate the agent's ID
    db.session.commit()

    if agent_with_config.agent_type == "Don't Maintain Task Queue":
        agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.name=="Goal Based Agent").first()
        print(agent_template)
        db_agent.agent_template_id = agent_template.id
    elif agent_with_config.agent_type == "Maintain Task Queue":
        agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.name=="Task Queue Agent With Seed").first()
        db_agent.agent_template_id = agent_template.id
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
        "memory_window": agent_with_config.memory_window,
        "max_iterations":agent_with_config.max_iterations

    }


    agent_configurations = [
        AgentConfiguration(agent_id=db_agent.id, key=key, value=str(value))
        for key, value in agent_config_values.items()
    ]

    db.session.add_all(agent_configurations)
    start_step_id = AgentTemplate.fetch_trigger_step_id(db.session, db_agent.agent_template_id)
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
