import requests
from fastapi import APIRouter, Body
from fastapi import HTTPException, Depends, Query
from fastapi_sqlalchemy import db
from superagi.config.config import get_config
from superagi.helper.auth import get_user_organisation
from superagi.helper.tool_helper import get_readme_content_from_code_link, download_tool, process_files
from superagi.helper.validator_helper import validate_github_link
from superagi.models.organisation import Organisation
from superagi.models.tool import Tool
from superagi.models.tool_kit import ToolKit
from superagi.types.common import GitHubLinkRequest

router = APIRouter()

marketplace_url = "https://app.superagi.com/api/"
# marketplace_url = "http://localhost:8001/"


@router.get("/marketplace/list")
def get_marketplace_tool_kits(page=0):
    """Get all marketplace agent templates"""
    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    page_size = 30
    tool_kits = db.session.query(ToolKit).filter(ToolKit.organisation_id == organisation_id).offset(
        page * page_size).limit(page_size).all()

    for tool_kit in tool_kits:
        tool_kit.tools = db.session.query(Tool).filter(Tool.tool_kit_id == tool_kit.id)
    return tool_kits


@router.get("/marketplace/details/{tool_kit_name}")
def get_marketplace_tool_kit_detail(tool_kit_name: str):
    """Get tool kit details from marketplace"""
    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    tool_kit = db.session.query(ToolKit).filter(ToolKit.organisation_id == organisation_id).first()
    return tool_kit


@router.get("/marketplace/readme/{tool_kit_name}")
def get_marketplace_tool_kit_readme(tool_kit_name: str):
    """Get tool kit readme from marketplace"""
    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    tool_kit = db.session.query(ToolKit).filter(ToolKit.name == tool_kit_name,
                                                Organisation.id == organisation_id).first()
    if not tool_kit:
        raise HTTPException(status_code=404, detail='ToolKit not found')
    return get_readme_content_from_code_link(tool_kit.tool_code_link)


@router.get("/marketplace/tools/{tool_kit_name}")
def get_marketplace_tool_kit_tools(tool_kit_name: str):
    """Get tool kit tools"""
    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    tool_kit = db.session.query(ToolKit).query(ToolKit.name == tool_kit_name).first()
    if not tool_kit:
        raise HTTPException(status_code=404, detail="ToolKit not found")
    tools = db.session.query(Tool).query(Tool.tool_kit_id == tool_kit.id).first()
    return tools


@router.get("/get/install/{tool_kit_name}")
def install_tool_kit(tool_kit_name: str):
    """Download and Install from marketplace"""
    # Check if the tool kit exists
    tool_kit = ToolKit.fetch_marketplace_detail(search_str="details",
                                                tool_kit_name=tool_kit_name)

    download_and_install_tool(tool_kit.tool_code_link)
    return {"message": "ToolKit installed successfully"}


@router.get("/get/{tool_kit_name}")
def get_installed_toolkit_details(tool_kit_name: str,
                                  organisation: Organisation = Depends(get_user_organisation)):
    """Get a tool kit by its name along with the details of its tools"""
    print("ORG  : ", organisation.id)
    # Fetch the tool kit by its ID
    tool_kit = db.session.query(ToolKit).filter(ToolKit.name == tool_kit_name,
                                                Organisation.id == organisation.id).first()

    if not tool_kit:
        # Return an appropriate response if the tool kit doesn't exist
        raise HTTPException(status_code=404, detail='ToolKit not found')

    print("Tool kit id", tool_kit)
    # Fetch the tools associated with the tool kit
    tools = db.session.query(Tool).filter(Tool.tool_kit_id == tool_kit.id).all()
    print("Tools", tools)
    # Add the tools to the tool kit object
    tool_kit.tools = tools
    # readme_content = get_readme(tool_kit.tool_code_link)
    return tool_kit


@router.post("/get/local/install", status_code=200)
def download_and_install_tool(github_link: GitHubLinkRequest = Body(...),
                              organisation: Organisation = Depends(get_user_organisation)):
    """From GitHub link install tool locally"""
    print(github_link)
    github_link = github_link.github_link
    if not validate_github_link(github_link):
        raise HTTPException(status_code=400, detail="Invalid Github link")
    download_folder = get_config("TOOLS_DIR")
    download_tool(github_link, download_folder)
    process_files(download_folder, db.session, organisation, code_link=github_link)


@router.get("/get/readme/{tool_kit_name}")
def get_installed_toolkit_readme(tool_kit_name: str, organisation: Organisation = Depends(get_user_organisation)):
    """Get Readme of a toolkit"""
    tool_kit = db.session.query(ToolKit).filter(ToolKit.name == tool_kit_name,
                                                Organisation.id == organisation.id).first()
    if not tool_kit:
        raise HTTPException(status_code=404, detail='ToolKit not found')
    readme_content = get_readme_content_from_code_link(tool_kit.tool_code_link)
    return readme_content


@router.get("/get")
def handle_marketplace_operations(
        search_str: str = Query(None, title="Search String"),
        tool_kit_name: str = Query(None, title="Tool Kit Name")
):
    """Handle marketplace operations"""
    response = ToolKit.fetch_marketplace_detail(search_str, tool_kit_name)
    return response
