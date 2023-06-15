from datetime import datetime
from typing import Annotated

from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Body
from fastapi_jwt_auth import AuthJWT

from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.worker import execute_agent
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.helper.auth import check_auth

router = APIRouter()


@router.get("/get/{agent_execution_permission_id}")
def get_agent_execution_permission(agent_execution_permission_id: int,
                                   Authorize: AuthJWT = Depends(check_auth)):
    """Get an agent execution permission by agent_execution_permission_id"""

    db_agent_execution_permission = db.session.query(AgentExecutionPermission).get(agent_execution_permission_id)
    if not db_agent_execution_permission:
        raise HTTPException(status_code=404, detail="Agent execution permission not found")
    return db_agent_execution_permission


@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentExecutionPermission))
def create_agent_execution_permission(
        agent_execution_permission: sqlalchemy_to_pydantic(AgentExecutionPermission, exclude=["id"])
        , Authorize: AuthJWT = Depends(check_auth)):
    """Create a new agent execution permission"""

    new_agent_execution_permission = AgentExecutionPermission(**agent_execution_permission.dict())
    db.session.add(new_agent_execution_permission)
    db.session.commit()
    return new_agent_execution_permission


@router.patch("/update/{agent_execution_permission_id}",
              response_model=sqlalchemy_to_pydantic(AgentExecutionPermission, exclude=["id"]))
def update_agent_execution_permission(agent_execution_permission_id: int,
                                      agent_execution_permission: sqlalchemy_to_pydantic(AgentExecutionPermission,
                                                                                         exclude=["id"]),
                                      Authorize: AuthJWT = Depends(check_auth)):
    """Update a particular execution permission"""

    db_agent_execution_permission = db.session.query(AgentExecutionPermission).get(agent_execution_permission_id)
    if not db_agent_execution_permission:
        raise HTTPException(status_code=404, detail="Agent execution permission not found")

    for key, value in agent_execution_permission.dict().items():
        setattr(db_agent_execution_permission, key, value)

    db.session.commit()
    return db_agent_execution_permission


@router.put("/update/status/{agent_execution_permission_id}")
def update_agent_execution_permission(agent_execution_permission_id: int,
                                      status: Annotated[bool, Body(embed=True)],
                                      response: Annotated[str, Body(embed=True)] = "",
                                      Authorize: AuthJWT = Depends(check_auth)):
    """Update a particular execution permission"""

    agent_execution_permission = db.session.query(AgentExecutionPermission).get(agent_execution_permission_id)
    print(agent_execution_permission)
    if agent_execution_permission is None:
        raise HTTPException(status_code=400, detail="Invalid Request")
    if status is None:
        raise HTTPException(status_code=400, detail="Invalid Request status is required")
    agent_execution_permission.status = status
    agent_execution_permission.response = response.strip() if len(response.strip()) > 0 else None
    db.session.commit()

    execute_agent.delay(agent_execution_permission.agent_execution_id, datetime.now())

    return {"success": True}
