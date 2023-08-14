from typing import Optional

import requests
from fastapi import APIRouter, Body
from fastapi import HTTPException, Depends, Query
from fastapi_sqlalchemy import db
from superagi.config.config import get_config
from superagi.helper.auth import get_user_organisation
from superagi.helper.tool_helper import get_readme_content_from_code_link, download_tool, process_files, \
    add_tool_to_json
from superagi.helper.github_helper import GithubHelper
from superagi.models.organisation import Organisation
from superagi.models.tool import Tool
from superagi.models.tool_config import ToolConfig
from superagi.models.toolkit import Toolkit
from superagi.types.common import GitHubLinkRequest
from superagi.helper.tool_helper import compare_toolkit
from superagi.helper.encyption_helper import decrypt_data, is_encrypted

router = APIRouter()


# marketplace_url = "https://app.superagi.com/api"
# marketplace_url = "http://localhost:8001/"


# For internal use
@router.get("/marketplace/list/{page}")
def get_marketplace_toolkits(
        page: int = 0,
):
    """
    Get marketplace tool kits.

    Args:
        page (int): The page number for pagination.

    Returns:
        list: A list of tool kits in the marketplace.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    page_size = 30

    # Apply search filter if provided
    query = db.session.query(Toolkit).filter(Toolkit.organisation_id == organisation_id)

    # Paginate the results
    toolkits = query.offset(page * page_size).limit(page_size).all()

    # Fetch tools for each tool kit
    for toolkit in toolkits:
        toolkit.tools = db.session.query(Tool).filter(Tool.toolkit_id == toolkit.id).all()
        toolkit.updated_at = toolkit.updated_at.strftime('%d-%b-%Y').upper()
    return toolkits


# For internal use
@router.get("/marketplace/details/{toolkit_name}")
def get_marketplace_toolkit_detail(toolkit_name: str):
    """
    Get tool kit details from the marketplace.

    Args:
        toolkit_name (str): The name of the tool kit.

    Returns:
        Toolkit: The tool kit details from the marketplace.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    toolkit = db.session.query(Toolkit).filter(Toolkit.organisation_id == organisation_id,
                                               Toolkit.name == toolkit_name).first()
    toolkit.tools = db.session.query(Tool).filter(Tool.toolkit_id == toolkit.id).all()
    toolkit.configs = db.session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit.id).all()
    for tool_configs in toolkit.configs:
        if is_encrypted(tool_configs.value):
            tool_configs.value = decrypt_data(tool_configs.value)
    return toolkit


# For internal use
@router.get("/marketplace/readme/{toolkit_name}")
def get_marketplace_toolkit_readme(toolkit_name: str):
    """
    Get tool kit readme from the marketplace.

    Args:
        toolkit_name (str): The name of the tool kit.

    Returns:
        str: The content of the tool kit's readme file.

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    toolkit = db.session.query(Toolkit).filter(Toolkit.name == toolkit_name,
                                               Toolkit.organisation_id == organisation_id).first()
    if not toolkit:
        raise HTTPException(status_code=404, detail='ToolKit not found')
    return get_readme_content_from_code_link(toolkit.tool_code_link)


# For internal use
@router.get("/marketplace/tools/{toolkit_name}")
def get_marketplace_toolkit_tools(toolkit_name: str):
    """
    Get tools of a specific tool kit from the marketplace.

    Args:
        toolkit_name (str): The name of the tool kit.

    Returns:
        Tool: The tools associated with the tool kit.

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    toolkit = db.session.query(Toolkit).filter(Toolkit.name == toolkit_name,
                                               Toolkit.organisation_id == organisation_id).first()
    if not toolkit:
        raise HTTPException(status_code=404, detail="ToolKit not found")
    tools = db.session.query(Tool).filter(Tool.toolkit_id == toolkit.id).first()
    return tools


@router.get("/get/install/{toolkit_name}")
def install_toolkit_from_marketplace(toolkit_name: str,
                                     organisation: Organisation = Depends(get_user_organisation)):
    """
    Download and install a tool kit from the marketplace.

    Args:
        toolkit_name (str): The name of the tool kit.
        organisation (Organisation): The user's organisation.

    Returns:
        dict: A message indicating the successful installation of the tool kit.

    """
    # Check if the tool kit exists
    toolkit = Toolkit.fetch_marketplace_detail(search_str="details",
                                               toolkit_name=toolkit_name)
    db_toolkit = Toolkit.add_or_update(session=db.session, name=toolkit['name'], description=toolkit['description'],
                                       tool_code_link=toolkit['tool_code_link'], organisation_id=organisation.id,
                                       show_toolkit=toolkit['show_toolkit'])
    for tool in toolkit['tools']:
        Tool.add_or_update(session=db.session, tool_name=tool['name'], description=tool['description'],
                           folder_name=tool['folder_name'], class_name=tool['class_name'], file_name=tool['file_name'],
                           toolkit_id=db_toolkit.id)
    for config in toolkit['configs']:
        ToolConfig.add_or_update(session=db.session, toolkit_id=db_toolkit.id, key=config['key'], value=config['value'])
    return {"message": "ToolKit installed successfully"}


@router.get("/get/toolkit_name/{toolkit_name}")
def get_installed_toolkit_details(toolkit_name: str,
                                  organisation: Organisation = Depends(get_user_organisation)):
    """
    Get details of a locally installed tool kit by its name, including the details of its tools.

    Args:
        toolkit_name (str): The name of the tool kit.
        organisation (Organisation): The user's organisation.

    Returns:
        Toolkit: The tool kit object with its associated tools.

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.

    """

    # Fetch the tool kit by its ID
    toolkit = db.session.query(Toolkit).filter(Toolkit.name == toolkit_name,
                                               Organisation.id == organisation.id).first()

    if not toolkit:
        # Return an appropriate response if the tool kit doesn't exist
        raise HTTPException(status_code=404, detail='ToolKit not found')

    # Fetch the tools associated with the tool kit
    tools = db.session.query(Tool).filter(Tool.toolkit_id == toolkit.id).all()
    # Add the tools to the tool kit object
    toolkit.tools = tools
    # readme_content = get_readme(toolkit.tool_code_link)
    return toolkit


@router.post("/get/local/install", status_code=200)
def download_and_install_tool(github_link_request: GitHubLinkRequest = Body(...),
                              organisation: Organisation = Depends(get_user_organisation)):
    """
    Install a tool locally from a GitHub link.

    Args:
        github_link_request (GitHubLinkRequest): The GitHub link request object.
        organisation (Organisation): The user's organisation.

    Returns:
        None

    Raises:
        HTTPException (status_code=400): If the GitHub link is invalid.

    """
    github_link = github_link_request.github_link
    if not GithubHelper.validate_github_link(github_link):
        raise HTTPException(status_code=400, detail="Invalid Github link")
    # download_folder = get_config("TOOLS_DIR")
    # download_tool(github_link, download_folder)
    # process_files(download_folder, db.session, organisation, code_link=github_link)
    add_tool_to_json(github_link)


@router.get("/get/readme/{toolkit_name}")
def get_installed_toolkit_readme(toolkit_name: str, organisation: Organisation = Depends(get_user_organisation)):
    """
    Get the readme content of a toolkit.

    Args:
        toolkit_name (str): The name of the toolkit.
        organisation (Organisation): The user's organisation.

    Returns:
        str: The readme content of the toolkit.

    Raises:
        HTTPException (status_code=404): If the toolkit is not found.

    """

    toolkit = db.session.query(Toolkit).filter(Toolkit.name == toolkit_name,
                                               Organisation.id == organisation.id).first()
    if not toolkit:
        raise HTTPException(status_code=404, detail='ToolKit not found')
    readme_content = get_readme_content_from_code_link(toolkit.tool_code_link)
    return readme_content


# Following APIs will be used to get marketplace related information
@router.get("/get")
def handle_marketplace_operations(
        search_str: str = Query(None, title="Search String"),
        toolkit_name: str = Query(None, title="Tool Kit Name")
):
    """
    Handle marketplace operations.

    Args:
        search_str (str, optional): The search string to filter toolkits. Defaults to None.
        toolkit_name (str, optional): The name of the toolkit. Defaults to None.

    Returns:
        dict: The response containing the marketplace details.

    """
    response = Toolkit.fetch_marketplace_detail(search_str, toolkit_name)
    return response


@router.get("/get/list")
def handle_marketplace_operations_list(
        page: int = Query(None, title="Page Number"),
        organisation: Organisation = Depends(get_user_organisation)
):
    """
    Handle marketplace operation list.

    Args:
        page (int, optional): The page number for pagination. Defaults to None.

    Returns:
        dict: The response containing the marketplace list.

    """

    marketplace_toolkits = Toolkit.fetch_marketplace_list(page=page)
    marketplace_toolkits_with_install = Toolkit.get_toolkit_installed_details(db.session, marketplace_toolkits,
                                                                              organisation)
    return marketplace_toolkits_with_install


@router.get("/get/local/list")
def get_installed_toolkit_list(organisation: Organisation = Depends(get_user_organisation)):
    """
    Get the list of installed tool kits.

    Args:
        organisation (Organisation): The organisation associated with the tool kits.

    Returns:
        list: The list of installed tool kits.

    """

    toolkits = db.session.query(Toolkit).filter(Toolkit.organisation_id == organisation.id).all()
    for toolkit in toolkits:
        toolkit_tools = db.session.query(Tool).filter(Tool.toolkit_id == toolkit.id).all()
        toolkit.tools = toolkit_tools

    return toolkits


@router.get("/check_update/{toolkit_name}")
def check_toolkit_update(toolkit_name: str, organisation: Organisation = Depends(get_user_organisation)):
    """
    Check if there is an update available for the installed tool kits.

    Returns:
        dict: The response containing the update details.

    """
    marketplace_toolkit = Toolkit.fetch_marketplace_detail(search_str="details",
                                                           toolkit_name=toolkit_name)
    if marketplace_toolkit is None:
        raise HTTPException(status_code=404, detail="Toolkit not found in marketplace")
    installed_toolkit = Toolkit.get_toolkit_from_name(db.session, toolkit_name, organisation)
    if installed_toolkit is None:
        return True
    installed_toolkit = installed_toolkit.to_dict()
    tools = Tool.get_toolkit_tools(db.session, installed_toolkit["id"])
    configs = ToolConfig.get_toolkit_tool_config(db.session, installed_toolkit["id"])
    installed_toolkit["configs"] = []
    installed_toolkit["tools"] = []

    for config in configs:
        installed_toolkit["configs"].append(config.to_dict())
    for tool in tools:
        installed_toolkit["tools"].append(tool.to_dict())

    return compare_toolkit(marketplace_toolkit, installed_toolkit)


@router.put("/update/{toolkit_name}")
def update_toolkit(toolkit_name: str, organisation: Organisation = Depends(get_user_organisation)):
    """
        Update the toolkit with the latest version from the marketplace.
    """
    marketplace_toolkit = Toolkit.fetch_marketplace_detail(search_str="details",
                                                           toolkit_name=toolkit_name)

    update_toolkit = Toolkit.add_or_update(
        db.session,
        name=marketplace_toolkit["name"],
        description=marketplace_toolkit["description"],
        show_toolkit=True if len(marketplace_toolkit["tools"]) > 1 else False,
        organisation_id=organisation.id,
        tool_code_link=marketplace_toolkit["tool_code_link"]
    )

    for tool in marketplace_toolkit["tools"]:
        Tool.add_or_update(db.session, tool_name=tool["name"], folder_name=tool["folder_name"],
                           class_name=tool["class_name"], file_name=tool["file_name"],
                           toolkit_id=update_toolkit.id, description=tool["description"])

    for tool_config_key in marketplace_toolkit["configs"]:
        ToolConfig.add_or_update(db.session, toolkit_id=update_toolkit.id,
                                 key=tool_config_key["key"])
