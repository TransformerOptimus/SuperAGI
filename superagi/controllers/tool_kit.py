from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db
from sqlalchemy.orm import Session
from superagi.models.tool_kit import ToolKit
from superagi.models.tool import Tool
from superagi.models.organisation import Organisation
from fastapi_jwt_auth import AuthJWT
from superagi.helper.auth import check_auth, get_user_organisation
from sqlalchemy.orm import joinedload
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
import requests
from fastapi import APIRouter
from typing import Any
from pydantic import BaseModel
from urllib.parse import urlparse



router = APIRouter()

MASTER_ORG_ID = 8


@router.post("/add", status_code=201)
def create_or_update_tool_kit(
        tool_kit_details: dict,
        Authorize: AuthJWT = Depends(check_auth),
):
    """Create or update a tool kit to register tool kit in Master DB store"""
    print(tool_kit_details)
    master_organisation = db.session.query(Organisation).filter(Organisation.id == MASTER_ORG_ID).first()
    if master_organisation is None:
        raise HTTPException(status_code=404,detail="Master Organisation not found!")
    print(master_organisation)
    # Check if the tool kit already exists
    existing_tool_kit = (
        db.session.query(ToolKit)
        .filter(ToolKit.name == tool_kit_details['name'], ToolKit.organisation_id == MASTER_ORG_ID)
        .first()
    )
    existing_tools = (
        db.session.query(Tool)
        .filter(Tool.tool_kit_id == existing_tool_kit.id)
        .all()
    )
    print(existing_tool_kit)
    show_tool_kit = False
    if len(tool_kit_details['tools']) > 1:
        show_tool_kit = True
    print(show_tool_kit)
    if existing_tool_kit is None:
        # New Tool Kit flow
        new_tool_kit = ToolKit(name=tool_kit_details['name'], description=tool_kit_details['description'],
                               show_tool_kit=show_tool_kit, organisation_id=MASTER_ORG_ID,
                               tool_code_link=tool_kit_details['tool_code_link'],
                               tool_readme_link=tool_kit_details['tool_readme_link'])
        db.session.add(new_tool_kit)
        db.session.commit()
        db.session.flush()

        print("New tool kit")
        print(new_tool_kit)
        # Populate Tools
        for tool in tool_kit_details['tools']:
            tool_kit_tool = Tool(name=tool['name'], description=tool['description'], tool_kit_id=new_tool_kit.id)
            db.session.add(tool_kit_tool)
            db.session.commit()
            db.session.flush()
            print("Tool : ")
            print(tool)
        return new_tool_kit

    if tool_kit_details['name'] is not None:
        existing_tool_kit.name = tool_kit_details['name']
    if tool_kit_details['description'] is not None:
        existing_tool_kit.description = tool_kit_details['description']
    if tool_kit_details['tool_code_link'] is not None:
        existing_tool_kit.tool_code_link = tool_kit_details['tool_code_link']
    if tool_kit_details['tool_readme_link'] is not None:
        existing_tool_kit.tool_readme_link = tool_kit_details['tool_readme_link']

    existing_tool_kit.show_tool_kit = show_tool_kit
    if tool_kit_details['tools'] is not None and len(tool_kit_details['tools']):
        # Update Tools
        print("Exisiting tools")
        print(existing_tools)
        existing_tool_names = {tool.name for tool in existing_tools}
        print("Updated")
        print(tool_kit_details['tools'])
        updated_tool_names = {tool['name'] for tool in tool_kit_details['tools']}

        # Delete tools that are not in the updated tool list
        tools_to_delete = existing_tool_names - updated_tool_names
        for tool in existing_tools:
            if tool.name in tools_to_delete:
                db.session.delete(tool)

        # Update existing tools and add new tools
        for tool_data in tool_kit_details['tools']:
            existing_tool = next((tool for tool in existing_tools if tool.name == tool_data['name']), None)

            if existing_tool:
                # Update existing tool if the description has changed
                if existing_tool.description != tool_data['description']:
                    existing_tool.description = tool_data['description']
            else:
                # Add new tool to the tool kit
                new_tool = Tool(
                    name=tool_data['name'],
                    description=tool_data['description'],
                    tool_kit_id=existing_tool_kit.id
                )
                db.session.add(new_tool)

        db.session.commit()
        db.session.refresh(existing_tool_kit)

        return existing_tool_kit


# Only to be used with master org - add security check
@router.get("/get/all")
def get_toolkits(Authorize: AuthJWT = Depends(check_auth)):
    """Get all toolkits of master organisation"""

    toolkits = db.session.query(ToolKit).filter(ToolKit.organisation_id == MASTER_ORG_ID).all()
    return toolkits


# def get_readme(githublink:str):
#     readme_url = "https://raw.githubusercontent.com/{username}/{repository}/{branch}/{folder}/README.md"
#     username = "TransformerOptimus"
#     repository = "your_repository"
#     branch = "main"  # or specify the branch you want to fetch from
#     folder = "your_folder"  # specify the folder path where the README.md is located
#
#     readme_url = readme_url.format(username=username, repository=repository, branch=branch, folder=folder)
#     response = requests.get(readme_url)
#     readme_content = response.text
#
#     return readme_content

# def get_readme(readme_url: str):
#     raw_url = readme_url.replace("github.com", "raw.githubusercontent.com")
#     raw_url = raw_url.replace("/blob/", "/")
#
#     response = requests.get(raw_url)
#     readme_content = response.text
#
#     return readme_content

def get_readme(repo_url: str):
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.split("/")

    # Extract username, repository, and branch from the URL
    username = path_parts[1]
    repository = path_parts[2]
    branch = path_parts[4] if len(path_parts) > 4 else "main"

    readme_url = f"https://raw.githubusercontent.com/{username}/{repository}/{branch}/README.md"
    response = requests.get(readme_url)
    if response.status_code == 404:
        readme_url = f"https://raw.githubusercontent.com/{username}/{repository}/{branch}/README.MD"
        response = requests.get(readme_url)
    readme_content = response.text
    return readme_content


@router.get("/get/{tool_kit_id}")
def get_tookit_by_master_organisation_and_tookit_id(tool_kit_id: int,
                                                    Authorize: AuthJWT = Depends(check_auth)):
    """Get a tool kit by its ID along with the details of its tools"""

    # Fetch the tool kit by its ID
    tool_kit = db.session.query(ToolKit).filter(ToolKit.id == tool_kit_id, Organisation.id == MASTER_ORG_ID).first()

    if not tool_kit:
        # Return an appropriate response if the tool kit doesn't exist
        raise HTTPException(status_code=404, detail='ToolKit not found')

    # Fetch the tools associated with the tool kit
    tools = db.session.query(Tool).filter(Tool.tool_kit_id == tool_kit_id).all()

    # Add the tools to the tool kit object
    tool_kit.tools = tools
    print("Read me link")
    # readme_content = get_readme(tool_kit.tool_readme_link)
    readme_content = ""
    return {
        "tool_kit": tool_kit,
        "readme_content": readme_content
    }


@router.get("/install/{tool_kit_id}")
def install_tool_kit(tool_kit_id: int):
    # Check if the tool kit exists
    tool_kit = db.session.query(ToolKit).filter(ToolKit.id == tool_kit_id).first()
    if not tool_kit:
        raise HTTPException(status_code=404, detail='ToolKit not found')

    # Call the API to get the tool kit details
    api_url = f"http://api.example.com/get/{tool_kit_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        # Extract the tool kit data from the response
        tool_kit_data = response.json()

        # Create or update the tool kit in the local database
        tool_kit.name = tool_kit_data["name"]
        tool_kit.description = tool_kit_data["description"]
        tool_kit.show_tool_kit = tool_kit_data["show_tool_kit"]

        # Save the changes to the database
        db.session.commit()
        db.session.refresh(tool_kit)

        # Optionally, update the tools associated with the tool kit
        tools_data = tool_kit_data.get("tools")
        if tools_data:
            # Remove the existing tools associated with the tool kit
            db.session.query(Tool).filter(Tool.tool_kit_id == tool_kit_id).delete()

            # Create new tool instances and associate them with the tool kit
            for tool_data in tools_data:
                tool = Tool(
                    name=tool_data["name"],
                    folder_name=tool_data["folder_name"],
                    class_name=tool_data["class_name"],
                    file_name=tool_data["file_name"],
                    tool_kit_id=tool_kit.id
                )
                db.session.add(tool)

            # Save the changes to the database
            db.session.commit()

        #Call Install Method
        #Write to tool.json

        return {"message": "ToolKit installed successfully"}

    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching ToolKit details")
