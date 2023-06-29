from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from superagi.helper.auth import check_auth, get_user_organisation
from superagi.models.organisation import Organisation
from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit

router = APIRouter()


class ToolOut(BaseModel):
    id: int
    name: str
    folder_name: str
    class_name: str
    file_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ToolIn(BaseModel):
    name: str
    folder_name: str
    class_name: str
    file_name: str

    class Config:
        orm_mode = True

# CRUD Operations
@router.post("/add", response_model=ToolOut, status_code=201)
def create_tool(
        tool: ToolIn,
        Authorize: AuthJWT = Depends(check_auth),
):
    """
    Create a new tool.

    Args:
        tool (ToolIn): Tool data.

    Returns:
        Tool: The created tool.

    Raises:
        HTTPException (status_code=400): If there is an issue creating the tool.

    """

    db_tool = Tool(
        name=tool.name,
        folder_name=tool.folder_name,
        class_name=tool.class_name,
        file_name=tool.file_name,
    )
    db.session.add(db_tool)
    db.session.commit()
    return db_tool


@router.get("/get/{tool_id}", response_model=ToolOut)
def get_tool(
        tool_id: int,
        Authorize: AuthJWT = Depends(check_auth),
):
    """
    Get a particular tool details.

    Args:
        tool_id (int): ID of the tool.

    Returns:
        Tool: The tool details.

    Raises:
        HTTPException (status_code=404): If the tool with the specified ID is not found.

    """

    db_tool = db.session.query(Tool).filter(Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return db_tool


@router.get("/list")
def get_tools(
        organisation: Organisation = Depends(get_user_organisation)):
    """Get all tools"""
    toolkits = db.session.query(Toolkit).filter(Toolkit.organisation_id == organisation.id).all()
    tools = []
    for toolkit in toolkits:
        db_tools = db.session.query(Tool).filter(Tool.toolkit_id == toolkit.id).all()
        tools.extend(db_tools)
    return tools


@router.put("/update/{tool_id}", response_model=ToolOut)
def update_tool(
        tool_id: int,
        tool: ToolIn,
        Authorize: AuthJWT = Depends(check_auth),
):
    """
    Update a particular tool.

    Args:
        tool_id (int): ID of the tool.
        tool (ToolIn): Updated tool data.

    Returns:
        Tool: The updated tool details.

    Raises:
        HTTPException (status_code=404): If the tool with the specified ID is not found.

    """

    db_tool = db.session.query(Tool).filter(Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    db_tool.name = tool.name
    db_tool.folder_name = tool.folder_name
    db_tool.class_name = tool.class_name
    db_tool.file_name = tool.file_name

    db.session.add(db_tool)
    db.session.commit()
    return db_tool
