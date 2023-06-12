from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from superagi.helper.auth import check_auth
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_template import AgentTemplate
from superagi.models.agent_template_config import AgentTemplateConfig
from superagi.models.agent_workflow import AgentWorkflow

router = APIRouter()


@router.post("/create", status_code=201, response_model=sqlalchemy_to_pydantic(AgentTemplate))
def create_agent_template(agent_template: sqlalchemy_to_pydantic(AgentTemplate, exclude=["id"]),
                           Authorize: AuthJWT = Depends(check_auth)):
    """Creates an agent template"""

    agent_workflow = db.session.query(AgentWorkflow).get(agent_template.agent_workflow_id)

    if not agent_workflow:
        raise HTTPException(status_code=404, detail="Agent Workflow not found")
    db_agent_template = AgentTemplate(agent_workflow_id=agent_template.agent_workflow_id,
                                       name=agent_template.name,
                                       description=agent_template.description,
                                       agent_type=agent_workflow.agent_type)
    db.session.add(db_agent_template)
    db.session.commit()

    return db_agent_template


@router.get("/get/{agent_template_id}")
def get_agent_template(agent_template_id: int,
                        Authorize: AuthJWT = Depends(check_auth)):
    """Get particular agent_template details. All major configs goals, constraints, evaluation are shown in the frontend."""
    db_agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.id == agent_template_id).first()
    if not db_agent_template:
        raise HTTPException(status_code=404, detail="Agent execution not found")
    template = db_agent_template.to_json()
    configs = {}
    agent_template_configs = db.session.query(AgentTemplateConfig).filter(AgentTemplateConfig.agent_template_id == agent_template_id).all()
    for agent_template_config in agent_template_configs:
        configs[agent_template_config.key] = {"value": agent_template_config.value, "value_type": agent_template_config.value_type}
    template["configs"] = configs
    return template



@router.post("/update/{agent_template_id}", response_model=sqlalchemy_to_pydantic(AgentTemplate))
def update_agent_template(agent_template_id: int,
                           agent_configs: dict,
                           Authorize: AuthJWT = Depends(check_auth)):
    """Update agent template"""
    db_agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.id == agent_template_id).first()
    if db_agent_template is None:
        raise HTTPException(status_code=404, detail="Agent Template not found")

    for key, value in agent_configs.items():
        agent_template_config = db.session.query(AgentTemplateConfig).filter(AgentTemplateConfig.agent_template_id == agent_template_id, AgentTemplateConfig.key == key).first()
        if agent_template_config is None:
            # create the template config
            agent_template_config = AgentTemplateConfig(agent_template_id=agent_template_id, key=key)
        agent_template_config.value = value["value"]
        agent_template_config.value_type = value["value_type"]
        db.session.add(agent_template_config)
    db.session.commit()

    return db_agent_template

@router.get("/agent/{agent_id}/save_as_template")
def save_agent_as_template(agent_id: str,
                        Authorize: AuthJWT = Depends(check_auth)):
    """Save agent as template"""
    agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent_configurations = db.session.query(AgentConfiguration).filter_by(agent_id=agent_id).all()
    if not agent_configurations:
        raise HTTPException(status_code=404, detail="Agent configurations not found")
    agent_template = AgentTemplate(name=agent.name, description=agent.description, agent_type=agent.agent_type, agent_workflow_id=agent.agent_workflow_id)
    db.session.add(agent_template)
    db.session.commit()
    main_keys = AgentTemplate.main_keys()
    for agent_configuration in agent_configurations:
        if agent_configuration.key not in main_keys:
            continue
        agent_template_config = AgentTemplateConfig(agent_template_id=agent_template.id, key=agent_configuration.key, value=agent_configuration.value, value_type=agent_configuration.value_type)
        db.session.add(agent_template_config)
    db.session.commit()
    return agent_template

@router.get("/list")
def list_agent_templates(organisation_id: int, search_str="",
                         Authorize: AuthJWT = Depends(check_auth)):
    """Get all running state agents"""
    templates = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation_id).all()
    output_json = []
    for template in templates:
        output_json.append(template.to_json())
    return output_json
