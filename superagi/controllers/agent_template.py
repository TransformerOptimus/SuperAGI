from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from main import get_config
from superagi.controllers.types.agent_execution_config import AgentRunIn
from superagi.controllers.types.agent_publish_config import AgentPublish
from superagi.helper.auth import get_user_organisation
from superagi.helper.auth import get_current_user
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_template import AgentTemplate
from superagi.models.agent_template_config import AgentTemplateConfig
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.tool import Tool
import json
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
        agent_workflow = AgentWorkflow.find_by_id(db_agent_template.agent_workflow_id)
        for agent_template_config in agent_template_configs:
            config_value = AgentTemplate.eval_agent_config(agent_template_config.key, agent_template_config.value)
            configs[agent_template_config.key] = {"value": config_value}
        template["configs"] = configs
        template["agent_workflow_name"] = agent_workflow.name
    else:
        template = AgentTemplate.fetch_marketplace_detail(agent_template_id)

    return template


@router.put("/update_agent_template/{agent_template_id}", status_code=200)
def edit_agent_template(agent_template_id: int,
                        updated_agent_configs: dict,
                        organisation=Depends(get_user_organisation)):

    """
    Update the details of an agent template.

    Args:
        agent_template_id (int): The ID of the agent template to update.
        updated_agent_configs (dict): The updated agent configurations.
        organisation (Depends): Dependency to get the user organisation.

    Returns:
        HTTPException (status_code=200): If the agent gets successfully edited.

    Raises:
        HTTPException (status_code=404): If the agent template is not found.
    """

    db_agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation.id,
                                                               AgentTemplate.id == agent_template_id).first()
    if db_agent_template is None:
        raise HTTPException(status_code=404, detail="Agent Template not found")

    agent_workflow = AgentWorkflow.find_by_name(db.session, updated_agent_configs["agent_configs"]["agent_workflow"])
    db_agent_template.name = updated_agent_configs["name"]
    db_agent_template.description = updated_agent_configs["description"]
    db_agent_template.agent_workflow_id = agent_workflow.id

    db.session.commit()

    agent_config_values = updated_agent_configs.get('agent_configs', {})

    for key, value in agent_config_values.items():
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        config = db.session.query(AgentTemplateConfig).filter(
            AgentTemplateConfig.agent_template_id == agent_template_id,
            AgentTemplateConfig.key == key
        ).first()

        if config is not None:
            config.value = value
        else:
            new_config = AgentTemplateConfig(
                agent_template_id=agent_template_id,
                key=key,
                value= value
            )
            db.session.add(new_config)

    db.session.commit()
    db.session.flush()

# @router.put("/update_agent_template/{agent_template_id}", status_code=200)
# def edit_agent_template(agent_template_id: int,
#                         updated_agent_configs: dict,
#                         organisation=Depends(get_user_organisation)):
    
#     """
#     Update the details of an agent template.

#     Args:
#         agent_template_id (int): The ID of the agent template to update.
#         edited_agent_configs (dict): The updated agent configurations.
#         organisation (Depends): Dependency to get the user organisation.

#     Returns:
#         HTTPException (status_code=200): If the agent gets successfully edited.

#     Raises:
#         HTTPException (status_code=404): If the agent template is not found.
#     """
    
#     db_agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.organisation_id == organisation.id,
#                                                                AgentTemplate.id == agent_template_id).first()
#     if db_agent_template is None:
#         raise HTTPException(status_code=404, detail="Agent Template not found")
    
#     db_agent_template.name = updated_agent_configs["name"]
#     db_agent_template.description = updated_agent_configs["description"]

#     db.session.commit()

#     agent_config_values = updated_agent_configs.get('agent_configs', {})

#     for key, value in agent_config_values.items():
#         if isinstance(value, (list, dict)):
#             value = json.dumps(value)
#         config = db.session.query(AgentTemplateConfig).filter(
#             AgentTemplateConfig.agent_template_id == agent_template_id,
#             AgentTemplateConfig.key == key
#         ).first()

#         if config is not None:
#             config.value = value
#         else:
#             new_config = AgentTemplateConfig(
#                 agent_template_id=agent_template_id,
#                 key=key,
#                 value= value
#             )
#             db.session.add(new_config)

#     db.session.commit()
#     db.session.flush()


@router.post("/save_agent_as_template/agent_id/{agent_id}/agent_execution_id/{agent_execution_id}")
def save_agent_as_template(agent_execution_id: str,
                           agent_id: str,
                           organisation=Depends(get_user_organisation)):
    """
    Save an agent as a template.

    Args:
        agent_id (str): The ID of the agent to save as a template.
        agent_execution_id (str): The ID of the agent execution to save as a template.
        organisation (Depends): Dependency to get the user organisation.

    Returns:
        dict: The saved agent template.

    Raises:
        HTTPException (status_code=404): If the agent or agent execution configurations are not found.
    """

    if agent_execution_id == 'undefined':
        raise HTTPException(status_code = 404, detail = "Agent Execution Id undefined")
    if agent_id == 'undefined':
        raise HTTPException(status_code = 404, detail = "Agent Id undefined")

    agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    configs = None

    if agent_execution_id == "-1":
        configs = db.session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id).all()
        if not configs:
            raise HTTPException(status_code=404, detail="Agent configurations not found")    
    else:
        configs = db.session.query(AgentExecutionConfiguration).filter(AgentExecutionConfiguration.agent_execution_id == agent_execution_id).all()
        if not configs:
            raise HTTPException(status_code=404, detail="Agent execution configurations not found")

    if configs is None:
        raise HTTPException(status_code=404, detail="Configurations not found")
    
    agent_template = AgentTemplate(name=agent.name, description=agent.description,
                                   agent_workflow_id=agent.agent_workflow_id,
                                   organisation_id=organisation.id)
    db.session.add(agent_template)
    db.session.commit()

    for config in configs:
            config_value = config.value
            if config.key not in AgentTemplate.main_keys():
                continue
            if config.key == "tools":
                config_value = str(Tool.convert_tool_ids_to_names(db, eval(config.value)))
            agent_template_config = AgentTemplateConfig(agent_template_id=agent_template.id, key=config.key,
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
        print(local_templates_hash)
        templates = AgentTemplate.fetch_marketplace_list(search_str, page)
        print(templates)
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

    if "constraints" not in template_config_dict:
        template_config_dict["constraints"] = []

    for key in main_keys:
        if key not in template_config_dict:
            template_config_dict[key] = ""

    template_config_dict["agent_template_id"] = agent_template.id
    agent_workflow = AgentWorkflow.find_by_id(db.session, agent_template.agent_workflow_id)
    template_config_dict["agent_workflow"] = agent_workflow.name

    return template_config_dict


@router.post("/publish_template/agent_execution_id/{agent_execution_id}", status_code=201)
def publish_template(agent_execution_id: str, organisation=Depends(get_user_organisation), user=Depends(get_current_user)):

    """
    Publish an agent execution as a template.

    Args:
        agent_execution_id (str): The ID of the agent execution to save as a template.
        organisation (Depends): Dependency to get the user organisation.
        user (Depends): Dependency to get the user.

    Returns:
        dict: The saved agent template.

    Raises:
        HTTPException (status_code=404): If the agent or agent execution configurations are not found.
    """
    
    if agent_execution_id == 'undefined':
        raise HTTPException(status_code = 404, detail = "Agent Execution Id undefined")

    agent_executions = AgentExecution.get_agent_execution_from_id(db.session, agent_execution_id)
    if agent_executions is None:
        raise HTTPException(status_code = 404, detail = "Agent Execution not found")
    agent_id = agent_executions.agent_id

    agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent_execution_configurations = db.session.query(AgentExecutionConfiguration).filter(AgentExecutionConfiguration.agent_execution_id == agent_execution_id).all()
    if not agent_execution_configurations:
        raise HTTPException(status_code=404, detail="Agent execution configurations not found")

    agent_template = AgentTemplate(name=agent.name, description=agent.description,
                                   agent_workflow_id=agent.agent_workflow_id,
                                   organisation_id=organisation.id)
    db.session.add(agent_template)
    db.session.commit()

    main_keys = AgentTemplate.main_keys()
    for agent_execution_configuration in agent_execution_configurations:
        config_value = agent_execution_configuration.value
        if agent_execution_configuration.key not in main_keys:
            continue
        if agent_execution_configuration.key == "tools":
            config_value = str(Tool.convert_tool_ids_to_names(db, eval(agent_execution_configuration.value)))
        agent_template_config = AgentTemplateConfig(agent_template_id=agent_template.id, key=agent_execution_configuration.key,
                                                    value=config_value)
        db.session.add(agent_template_config)

    agent_template_configs = [
    AgentTemplateConfig(agent_template_id=agent_template.id, key="status", value="UNDER REVIEW"),
    AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Name", value=user.name),
    AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Email", value=user.email)]
    db.session.add_all(agent_template_configs)

    db.session.commit()
    db.session.flush()
    return agent_template.to_dict()

@router.post("/publish_template", status_code=201)
def handle_publish_template(updated_details: AgentPublish, organisation=Depends(get_user_organisation), user=Depends(get_current_user)):
    
    """
    Publish a template from edit template page.

    Args:
        organisation (Depends): Dependency to get the user organisation.
        user (Depends): Dependency to get the user.

    Returns:
        dict: The saved agent template.

    Raises:
        HTTPException (status_code=404): If the agent template or workflow are not found.
    """

    old_template_id = updated_details.agent_template_id
    old_agent_template = db.session.query(AgentTemplate).filter(AgentTemplate.id==old_template_id, AgentTemplate.organisation_id==organisation.id).first()
    if old_agent_template is None:
        raise HTTPException(status_code = 404, detail = "Agent Template not found")
    agent_workflow_id = old_agent_template.agent_workflow_id
    if agent_workflow_id is None:
        raise HTTPException(status_code = 404, detail = "Agent Workflow not found")
    
    agent_template = AgentTemplate(name=updated_details.name, description=updated_details.description,
                                   agent_workflow_id=agent_workflow_id,
                                   organisation_id=organisation.id)
    db.session.add(agent_template)
    db.session.commit()

    agent_template_configs = {
        "goal": updated_details.goal,
        "instruction": updated_details.instruction,
        "constraints": updated_details.constraints,
        "toolkits": updated_details.toolkits,
        "exit": updated_details.exit,
        "tools": updated_details.tools,
        "iteration_interval": updated_details.iteration_interval,
        "model": updated_details.model,
        "permission_type": updated_details.permission_type,
        "LTM_DB": updated_details.LTM_DB,
        "max_iterations": updated_details.max_iterations,
        "user_timezone": updated_details.user_timezone,
        "knowledge": updated_details.knowledge
    }

    for key, value in agent_template_configs.items():
        if key == "tools":
            value = Tool.convert_tool_ids_to_names(db, value)
        agent_template_config = AgentTemplateConfig(agent_template_id=agent_template.id, key=key, value=str(value))
        db.session.add(agent_template_config)

    agent_template_configs = [
    AgentTemplateConfig(agent_template_id=agent_template.id, key="status", value="UNDER REVIEW"),
    AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Name", value=user.name),
    AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Email", value=user.email)]
    db.session.add_all(agent_template_configs)

    db.session.commit()
    db.session.flush()
    return agent_template.to_dict()