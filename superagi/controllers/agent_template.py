from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from main import get_config
from superagi.helper.auth import get_user_organisation
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_template import AgentTemplate
from superagi.models.agent_template_config import AgentTemplateConfig
from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.tool import Tool
# from superagi.types.db import AgentTemplateIn, AgentTemplateOut

router = APIRouter()


class AgentTemplateOut(BaseModel):
    id: int
    organisation_id: int
    agent_workflow_id: int
    name: str
    description: str
    marketplace_template_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AgentTemplateIn(BaseModel):
    organisation_id: int
    agent_workflow_id: int
    name: str
    description: str
    marketplace_template_id: int

    class Config:
        orm_mode = True

@router.post("/create", status_code=201, response_model=AgentTemplateOut)
def create_agent_template(agent_template: AgentTemplateIn,
                          organisation=Depends(get_user_organisation)):
    """
    Create an agent template.

    Args:
        agent_template (AgentTemplate): Data for creating an agent template.
        organisation (Depends): Dependency to get the user organisation.

    Returns:
        AgentTemplate: The created agent template.

    Raises:
        HTTPException (status_code=404): If the associated agent workflow is not found.
    """

    agent_workflow = db.session.query(AgentWorkflow).get(agent_template.agent_workflow_id)

    if not agent_workflow:
        raise HTTPException(status_code=404, detail="Agent Workflow not found")
    db_agent_template = AgentTemplate(agent_workflow_id=agent_template.agent_workflow_id,
                                      name=agent_template.name,
                                      organisation_id=organisation.id,
                                      description=agent_template.description)
    db.session.add(db_agent_template)
    db.session.commit()

    return db_agent_template


@router.get("/get/{agent_template_id}")
def get_agent_template(template_source, agent_template_id: int, organisation=Depends(get_user_organisation)):
    """
        Get the details of a specific agent template.

        Args:
            template_source (str): The source of the agent template ("local" or "marketplace").
            agent_template_id (int): The ID of the agent template.
            organisation (Depends): Dependency to get the user organisation.

        Returns:
            dict: The details of the agent template.

        Raises:
            HTTPException (status_code=404): If the agent template is not found.
    """
    if template_source == "local":
        db_agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation.id,
                                                                   AgentTemplate.id == agent_template_id).first()
        if not db_agent_template:
            raise HTTPException(status_code=404, detail="Agent execution not found")
        template = db_agent_template.to_dict()
        configs = {}
        agent_template_configs = db.session.query(AgentTemplateConfig).filter(
            AgentTemplateConfig.agent_template_id == agent_template_id).all()
        for agent_template_config in agent_template_configs:
            config_value = AgentTemplate.eval_agent_config(agent_template_config.key, agent_template_config.value)
            configs[agent_template_config.key] = {"value": config_value}
        template["configs"] = configs
    else:
        template = AgentTemplate.fetch_marketplace_detail(agent_template_id)

    return template


@router.post("/update_details/{agent_template_id}", response_model=AgentTemplateOut)
def update_agent_template(agent_template_id: int,
                          agent_configs: dict,
                          organisation=Depends(get_user_organisation)):
    """
    Update the details of an agent template.

    Args:
        agent_template_id (int): The ID of the agent template to update.
        agent_configs (dict): The updated agent configurations.
        organisation (Depends): Dependency to get the user organisation.

    Returns:
        dict: The updated agent template.

    Raises:
        HTTPException (status_code=404): If the agent template is not found.
    """

    db_agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation.id,
                                                               AgentTemplate.id == agent_template_id).first()
    if db_agent_template is None:
        raise HTTPException(status_code=404, detail="Agent Template not found")

    for key, value in agent_configs.items():
        agent_template_config = db.session.query(AgentTemplateConfig).filter(
            AgentTemplateConfig.agent_template_id == agent_template_id, AgentTemplateConfig.key == key).first()
        if agent_template_config is None:
            # create the template config
            agent_template_config = AgentTemplateConfig(agent_template_id=agent_template_id, key=key)
        agent_template_config.value = value["value"]
        db.session.add(agent_template_config)
    db.session.commit()

    return db_agent_template


@router.post("/save_agent_as_template/{agent_id}")
def save_agent_as_template(agent_id: str,
                           organisation=Depends(get_user_organisation)):
    """
    Save an agent as a template.

    Args:
        agent_id (str): The ID of the agent to save as a template.
        organisation (Depends): Dependency to get the user organisation.

    Returns:
        dict: The saved agent template.

    Raises:
        HTTPException (status_code=404): If the agent or agent configurations are not found.
    """

    agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent_configurations = db.session.query(AgentConfiguration).filter_by(agent_id=agent_id).all()
    if not agent_configurations:
        raise HTTPException(status_code=404, detail="Agent configurations not found")
    agent_template = AgentTemplate(name=agent.name, description=agent.description,
                                   agent_workflow_id=agent.agent_workflow_id,
                                   organisation_id=organisation.id)
    db.session.add(agent_template)
    db.session.commit()
    main_keys = AgentTemplate.main_keys()
    for agent_configuration in agent_configurations:
        config_value = agent_configuration.value
        if agent_configuration.key not in main_keys:
            continue
        if agent_configuration.key == "tools":
            config_value = str(Tool.convert_tool_ids_to_names(db, eval(agent_configuration.value)))
        agent_template_config = AgentTemplateConfig(agent_template_id=agent_template.id, key=agent_configuration.key,
                                                    value=config_value)
        db.session.add(agent_template_config)
    db.session.commit()
    db.session.flush()
    return agent_template.to_dict()


@router.get("/list")
def list_agent_templates(template_source="local", search_str="", page=0, organisation=Depends(get_user_organisation)):
    """
        List agent templates.

        Args:
            template_source (str, optional): The source of the templates ("local" or "marketplace"). Defaults to "local".
            search_str (str, optional): The search string to filter templates. Defaults to "".
            page (int, optional): The page number for paginated results. Defaults to 0.
            organisation (Depends): Dependency to get the user organisation.

        Returns:
            list: A list of agent templates.
    """

    output_json = []
    if template_source == "local":
        templates = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation.id).all()
        for template in templates:
            template.updated_at = template.updated_at.strftime('%d-%b-%Y').upper()
            output_json.append(template)
    else:
        local_templates = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation.id,
                                                                 AgentTemplate.marketplace_template_id != None).all()
        local_templates_hash = {}
        for local_template in local_templates:
            local_templates_hash[local_template.marketplace_template_id] = True
        templates = AgentTemplate.fetch_marketplace_list(search_str, page)

        for template in templates:
            template["is_installed"] = local_templates_hash.get(template["id"], False)
            template["organisation_id"] = organisation.id
            output_json.append(template)

    return output_json


@router.get("/marketplace/list")
def list_marketplace_templates(page=0):
    """
    Get all marketplace agent templates.

    Args:
        page (int, optional): The page number for paginated results. Defaults to 0.

    Returns:
        list: A list of marketplace agent templates.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    page_size = 30
    templates = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation_id).offset(
        page * page_size).limit(page_size).all()
    output_json = []
    for template in templates:
        template.updated_at = template.updated_at.strftime('%d-%b-%Y').upper()
        output_json.append(template)
    return output_json


@router.get("/marketplace/template_details/{agent_template_id}")
def marketplace_template_detail(agent_template_id):
    """
    Get marketplace template details.

    Args:
        agent_template_id (int): The ID of the marketplace agent template.

    Returns:
        dict: A dictionary containing the marketplace template details.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    template = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation_id,
                                                      AgentTemplate.id == agent_template_id).first()
    template_configs = db.session.query(AgentTemplateConfig).filter(
        AgentTemplateConfig.agent_template_id == template.id).all()

    workflow = db.session.query(AgentWorkflow).filter(AgentWorkflow.id == template.agent_workflow_id).first()
    tool_configs = {}
    for template_config in template_configs:
        config_value = AgentTemplate.eval_agent_config(template_config.key, template_config.value)
        tool_configs[template_config.key] = {"value": config_value}
    output_json = {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "agent_workflow_id": template.agent_workflow_id,
        "agent_workflow_name": workflow.name,
        "configs": tool_configs
    }
    return output_json


@router.post("/download", status_code=201)
def download_template(agent_template_id: int,
                      organisation=Depends(get_user_organisation)):
    """
    Create a new agent with configurations.

    Args:
        agent_template_id (int): The ID of the agent template.
        organisation: User's organisation.

    Returns:
        dict: A dictionary containing the details of the downloaded template.
    """
    template = AgentTemplate.clone_agent_template_from_marketplace(db, organisation.id, agent_template_id)
    return template.to_dict()


@router.get("/agent_config", status_code=201)
def fetch_agent_config_from_template(agent_template_id: int,
                                     organisation=Depends(get_user_organisation)):
    """
    Fetches agent configuration from a template.

    Args:
        agent_template_id (int): The ID of the agent template.
        organisation: User's organisation.

    Returns:
        dict: A dictionary containing the agent configuration fetched from the template.

    Raises:
        HTTPException: If the template is not found.
    """

    agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.id == agent_template_id,
                                                            AgentTemplate.organisation_id == organisation.id).first()
    if not agent_template:
        raise HTTPException(status_code=404, detail="Template not found")

    template_config = db.session.query(AgentTemplateConfig).filter(
        AgentTemplateConfig.agent_template_id == agent_template_id).all()
    template_config_dict = {}
    main_keys = AgentTemplate.main_keys()
    for config in template_config:
        if config.key in main_keys:
            template_config_dict[config.key] = AgentTemplate.eval_agent_config(config.key, config.value)
    if "instruction" not in template_config_dict:
        template_config_dict["instruction"] = []
    template_config_dict["agent_template_id"] = agent_template.id

    return template_config_dict
