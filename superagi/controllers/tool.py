from fastapi import APIRouter, Body
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.config.config import get_config
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.helper.tool_helper import download_tool
# from superagi.helper.tool_helper import process_files
from superagi.helper.validator_helper import validate_github_link
from superagi.models.organisation import Organisation
from superagi.models.tool import Tool
from superagi.models.tool_kit import ToolKit
from superagi.types.common import GitHubLinkRequest

router = APIRouter()


# CRUD Operations
# @router.post("/add", response_model=sqlalchemy_to_pydantic(Tool), status_code=201)
# def create_tool(
#         tool: sqlalchemy_to_pydantic(Tool, exclude=["id"]),
#         Authorize: AuthJWT = Depends(check_auth),
#         organisation: Organisation = Depends(get_user_organisation)
# ):
#     """Create a new tool"""
#
#     db_tool = Tool(
#         name=tool.name,
#         folder_name=tool.folder_name,
#         class_name=tool.class_name,
#         file_name=tool.file_name,
#     )
#
#     tool_kit = db.session.query(ToolKit).filter(ToolKit.name == tool.folder_name)
#
#     if tool.tool_kit_id is None:
#         new_tool_kit = ToolKit(name=tool.folder_name, description=f"Tool kit consists of {tool.name}",
#                                show_tool_kit=False, organisation_id={organisation.id})
#         db.session.add(new_tool_kit)
#         db.session.commit()
#         db.session.flush()
#         db_tool.tool_kit_id = new_tool_kit.id
#     else:
#         db_tool.tool_kit_id = tool.tool_kit_id
#
#     db.session.add(db_tool)
#     db.session.commit()
#     return db_tool


@router.get("/get/{tool_id}", response_model=sqlalchemy_to_pydantic(Tool))
def get_tool(
        tool_id: int,
        Authorize: AuthJWT = Depends(check_auth),
):
    """Get a particular tool details"""

    db_tool = db.session.query(Tool).filter(Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return db_tool


# @router.put("/update/{tool_id}", response_model=sqlalchemy_to_pydantic(Tool))
# def update_tool(
#         tool_id: int,
#         tool: sqlalchemy_to_pydantic(Tool, exclude=["id"]),
#         Authorize: AuthJWT = Depends(check_auth),
# ):
#     """Update a particular tool"""
#
#     db_tool = db.session.query(Tool).filter(Tool.id == tool_id).first()
#     if not db_tool:
#         raise HTTPException(status_code=404, detail="Tool not found")
#
#     if tool.name is not None:
#         db_tool.name = tool.name
#     if tool.folder_name is not None:
#         db_tool.folder_name = tool.folder_name
#     if tool.class_name is not None:
#         db_tool.class_name = tool.class_name
#     if tool.file_name is not None:
#         db_tool.file_name = tool.file_name
#     if tool.tool_kit_id is not None:
#         db_tool.tool_kit_id = tool.tool_kit_id
#
#     # db_tool.name = tool.name
#     # db_tool.folder_name = tool.folder_name
#     # db_tool.class_name = tool.class_name
#     # db_tool.file_name = tool.file_name
#
#     db.session.add(db_tool)
#     db.session.commit()
#     return db_tool


@router.get("/get")
def get_tools(Authorize: AuthJWT = Depends(check_auth),
              organisation: Organisation = Depends(get_user_organisation)):
    """Get all tools"""
    tool_kits = db.session.query(ToolKit).filter(ToolKit.organisation_id == organisation.id)
    tools = []
    for tool_kit in tool_kits:
        db_tools = db.session.query(Tool).filter(ToolKit.id == tool_kit.id).all()
        tools.extend(db_tools)
    return tools