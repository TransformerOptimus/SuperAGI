from typing import Optional

import requests
from fastapi import APIRouter, Body
from fastapi import HTTPException, Depends, Query
from fastapi_sqlalchemy import db
from superagi.config.config import get_config
from superagi.helper.auth import get_user_organisation
from superagi.helper.tool_helper import get_readme_content_from_code_link, download_tool,process_files,add_tool_to_json
from superagi.helper.validator_helper import validate_github_link
from superagi.models.organisation import Organisation
from superagi.models.tool import Tool
from superagi.models.tool_kit import ToolKit
from superagi.types.common import GitHubLinkRequest

router = APIRouter()


# marketplace_url = "https://app.superagi.com/api"
# marketplace_url = "http://localhost:8001/"


#For internal use
@router.get("/marketplace/list/{page}")
def get_marketplace_tool_kits(
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
    query = db.session.query(ToolKit).filter(ToolKit.organisation_id == organisation_id)

    # Paginate the results
    tool_kits = query.offset(page * page_size).limit(page_size).all()

    # Fetch tools for each tool kit
    for tool_kit in tool_kits:
        tool_kit.tools = db.session.query(Tool).filter(Tool.tool_kit_id == tool_kit.id).all()

    return tool_kits

#For internal use
@router.get("/marketplace/details/{tool_kit_name}")
def get_marketplace_tool_kit_detail(tool_kit_name: str):
    """
    Get tool kit details from the marketplace.

    Args:
        tool_kit_name (str): The name of the tool kit.

    Returns:
        ToolKit: The tool kit details from the marketplace.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    tool_kit = db.session.query(ToolKit).filter(ToolKit.organisation_id == organisation_id).first()
    return tool_kit

#For internal use
@router.get("/marketplace/readme/{tool_kit_name}")
def get_marketplace_tool_kit_readme(tool_kit_name: str):
    """
    Get tool kit readme from the marketplace.

    Args:
        tool_kit_name (str): The name of the tool kit.

    Returns:
        str: The content of the tool kit's readme file.

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    tool_kit = db.session.query(ToolKit).filter(ToolKit.name == tool_kit_name,
                                                Organisation.id == organisation_id).first()
    if not tool_kit:
        raise HTTPException(status_code=404, detail='ToolKit not found')
    return get_readme_content_from_code_link(tool_kit.tool_code_link)

#For internal use
@router.get("/marketplace/tools/{tool_kit_name}")
def get_marketplace_tool_kit_tools(tool_kit_name: str):
    """
    Get tools of a specific tool kit from the marketplace.

    Args:
        tool_kit_name (str): The name of the tool kit.

    Returns:
        Tool: The tools associated with the tool kit.

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    tool_kit = db.session.query(ToolKit).filter(ToolKit.name == tool_kit_name).first()
    if not tool_kit:
        raise HTTPException(status_code=404, detail="ToolKit not found")
    tools = db.session.query(Tool).filter(Tool.tool_kit_id == tool_kit.id).first()
    return tools


@router.get("/get/install/{tool_kit_name}")
def install_tool_kit_from_marketplace(tool_kit_name: str,
                                      organisation: Organisation = Depends(get_user_organisation)):
    """
    Download and install a tool kit from the marketplace.

    Args:
        tool_kit_name (str): The name of the tool kit.
        organisation (Organisation): The user's organisation.

    Returns:
        dict: A message indicating the successful installation of the tool kit.

    """

    # Check if the tool kit exists
    tool_kit = ToolKit.fetch_marketplace_detail(search_str="details",
                                                tool_kit_name=tool_kit_name)
    download_and_install_tool(GitHubLinkRequest(github_link=tool_kit['tool_code_link']),
                              organisation=organisation)
    return {"message": "ToolKit installed successfully"}


@router.get("/get/toolkit_name/{tool_kit_name}")
def get_installed_toolkit_details(tool_kit_name: str,
                                  organisation: Organisation = Depends(get_user_organisation)):
    """
    Get details of a locally installed tool kit by its name, including the details of its tools.

    Args:
        tool_kit_name (str): The name of the tool kit.
        organisation (Organisation): The user's organisation.

    Returns:
        ToolKit: The tool kit object with its associated tools.

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.

    """

    # Fetch the tool kit by its ID
    tool_kit = db.session.query(ToolKit).filter(ToolKit.name == tool_kit_name,
                                                Organisation.id == organisation.id).first()

    if not tool_kit:
        # Return an appropriate response if the tool kit doesn't exist
        raise HTTPException(status_code=404, detail='ToolKit not found')

    # Fetch the tools associated with the tool kit
    tools = db.session.query(Tool).filter(Tool.tool_kit_id == tool_kit.id).all()
    # Add the tools to the tool kit object
    tool_kit.tools = tools
    # readme_content = get_readme(tool_kit.tool_code_link)
    return tool_kit


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
    if not validate_github_link(github_link):
        raise HTTPException(status_code=400, detail="Invalid Github link")
    # download_folder = get_config("TOOLS_DIR")
    # download_tool(github_link, download_folder)
    # process_files(download_folder, db.session, organisation, code_link=github_link)
    add_tool_to_json(github_link)

@router.get("/get/readme/{tool_kit_name}")
def get_installed_toolkit_readme(tool_kit_name: str, organisation: Organisation = Depends(get_user_organisation)):
    """
    Get the readme content of a toolkit.

    Args:
        tool_kit_name (str): The name of the toolkit.
        organisation (Organisation): The user's organisation.

    Returns:
        str: The readme content of the toolkit.

    Raises:
        HTTPException (status_code=404): If the toolkit is not found.

    """

    tool_kit = db.session.query(ToolKit).filter(ToolKit.name == tool_kit_name,
                                                Organisation.id == organisation.id).first()
    if not tool_kit:
        raise HTTPException(status_code=404, detail='ToolKit not found')
    readme_content = get_readme_content_from_code_link(tool_kit.tool_code_link)
    return readme_content

# Following APIs will be used to get marketplace related information
@router.get("/get")
def handle_marketplace_operations(
        search_str: str = Query(None, title="Search String"),
        tool_kit_name: str = Query(None, title="Tool Kit Name")
):
    """
    Handle marketplace operations.

    Args:
        search_str (str, optional): The search string to filter toolkits. Defaults to None.
        tool_kit_name (str, optional): The name of the toolkit. Defaults to None.

    Returns:
        dict: The response containing the marketplace details.

    """
    response = ToolKit.fetch_marketplace_detail(search_str, tool_kit_name)
    return response


@router.get("/get/list")
def handle_marketplace_operations_list(
        page: int = Query(None, title="Page Number"),
):
    """
    Handle marketplace operation list.

    Args:
        page (int, optional): The page number for pagination. Defaults to None.

    Returns:
        dict: The response containing the marketplace list.

    """

    response = ToolKit.fetch_marketplace_list(page=page)
    return response


@router.get("/get/local/list")
def get_installed_tool_kit_list(organisation: Organisation = Depends(get_user_organisation)):
    """
    Get the list of installed tool kits.

    Args:
        organisation (Organisation): The organisation associated with the tool kits.

    Returns:
        list: The list of installed tool kits.

    """

    tool_kits = db.session.query(ToolKit).filter(ToolKit.organisation_id == organisation.id).all()
    for tool_kit in tool_kits:
        tool_kit_tools = db.session.query(Tool).filter(Tool.tool_kit_id == tool_kit.id).all()
        tool_kit.tools = tool_kit_tools

    return tool_kits