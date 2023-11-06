from datetime import datetime
from typing import Annotated

from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Body
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.worker import execute_agent
from fastapi import APIRouter

from superagi.helper.auth import check_auth
# from superagi.types.db import AgentExecutionPermissionOut, AgentExecutionPermissionIn

router = APIRouter()


class AgentExecutionPermissionOut(BaseModel):
    id: int
    agent_execution_id: int
    agent_id: int
    status: str
    tool_name: str
    user_feedback: str
    assistant_reply: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AgentExecutionPermissionIn(BaseModel):
    agent_execution_id: int
    agent_id: int
    status: str
    tool_name: str
    user_feedback: str
    assistant_reply: str

    class Config:
        orm_mode = True


@router.get("/get/{agent_execution_permission_id}")
def get_agent_execution_permission(agent_execution_permission_id: int,
                                   Authorize: AuthJWT = Depends(check_auth)):
    """
    Get an agent execution permission by its ID.

    Args:
        agent_execution_permission_id (int): The ID of the agent execution permission.
        Authorize (AuthJWT, optional): Authentication object. Defaults to Depends(check_auth).

    Raises:
        HTTPException: If the agent execution permission is not found.

    Returns:
        AgentExecutionPermission: The requested agent execution permission.
    """

    db_agent_execution_permission = db.session.query(AgentExecutionPermission).get(agent_execution_permission_id)
    if not db_agent_execution_permission:
        raise HTTPException(status_code=404, detail="Agent execution permission not found")
    return db_agent_execution_permission


@router.post("/add", response_model=AgentExecutionPermissionOut)
def create_agent_execution_permission(
        agent_execution_permission: AgentExecutionPermissionIn
        , Authorize: AuthJWT = Depends(check_auth)):
    """
    Create a new agent execution permission.

    Args:
        agent_execution_permission : An instance of AgentExecutionPermission model as json.
        Authorize (AuthJWT, optional): Authorization token, by default depends on the check_auth function.

    Returns:
        new_agent_execution_permission: A newly created agent execution permission instance.
    """
    new_agent_execution_permission = AgentExecutionPermission(**agent_execution_permission.dict())
    db.session.add(new_agent_execution_permission)
    db.session.commit()
    return new_agent_execution_permission


@router.patch("/update/{agent_execution_permission_id}",
              response_model=AgentExecutionPermissionIn)
def update_agent_execution_permission(agent_execution_permission_id: int,
                                      agent_execution_permission: AgentExecutionPermissionIn,
                                      Authorize: AuthJWT = Depends(check_auth)):
    """
    Update an AgentExecutionPermission in the database.

    Given an agent_execution_permission_id and the updated agent_execution_permission, this function updates the
    corresponding AgentExecutionPermission in the database. If the AgentExecutionPermission is not found, an HTTPException
    is raised.

    Args:
        agent_execution_permission_id (int): The ID of the AgentExecutionPermission to update.
        agent_execution_permission : The updated AgentExecutionPermission object as json.
        Authorize (AuthJWT, optional): Dependency to authenticate the user.

    Returns:
        db_agent_execution_permission (AgentExecutionPermission): The updated AgentExecutionPermission in the database.

    Raises:
        HTTPException: If the AgentExecutionPermission is not found in the database.
    """
    db_agent_execution_permission = db.session.query(AgentExecutionPermission).get(agent_execution_permission_id)
    if not db_agent_execution_permission:
        raise HTTPException(status_code=404, detail="Agent execution permission not found")

    for key, value in agent_execution_permission.dict().items():
        setattr(db_agent_execution_permission, key, value)

    db.session.commit()
    return db_agent_execution_permission


@router.put("/update/status/{agent_execution_permission_id}")
def update_agent_execution_permission_status(agent_execution_permission_id: int,
                                             status: Annotated[bool, Body(embed=True)],
                                             user_feedback: Annotated[str, Body(embed=True)] = "",
                                             Authorize: AuthJWT = Depends(check_auth)):
    """
    Update the execution permission status of an agent in the database.

    This function updates the execution permission status of an agent in the database. The status can be
    either "APPROVED" or "REJECTED". The function also updates the user feedback if provided,
    commits the changes to the database, and enqueues the agent for execution.

    :params:
    - agent_execution_permission_id (int): The ID of the agent execution permission
    - status (bool): The status of the agent execution permission, True for "APPROVED", False for "REJECTED"
    - user_feedback (str): Optional user feedback on the status update
    - Authorize (AuthJWT): Dependency function to check user authorization

    :return:
    - A dictionary containing a "success" key with the value True to indicate a successful update.
    """

    agent_execution_permission = db.session.query(AgentExecutionPermission).get(agent_execution_permission_id)
    print(agent_execution_permission)
    if agent_execution_permission is None:
        raise HTTPException(status_code=400, detail="Invalid Request")
    if status is None:
        raise HTTPException(status_code=400, detail="Invalid Request status is required")
    agent_execution_permission.status = "APPROVED" if status else "REJECTED"
    agent_execution_permission.user_feedback = user_feedback.strip() if len(user_feedback.strip()) > 0 else None
    db.session.commit()

    execute_agent.delay(agent_execution_permission.agent_execution_id, datetime.now())

    return {"success": True}
