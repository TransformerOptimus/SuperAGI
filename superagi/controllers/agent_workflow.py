from fastapi import APIRouter
from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from superagi.helper.agent_workflow import AgentWorkflowHelper
from superagi.helper.auth import get_user_organisation, check_auth

router = APIRouter()


class AgentWorkflowIn(BaseModel):
    name: str
    description: str
    code_yaml: str
    class Config:
        orm_mode = True


@router.get("/list", status_code=200)
def list_agent_workflows(organisation=Depends(get_user_organisation),
                         Authorize: AuthJWT = Depends(check_auth)):
    """
    Lists agent workflows.

    Args:
        organisation: User's organisation.

    Returns:
        list: A list of dictionaries representing the agent workflows.

    """
    return AgentWorkflowHelper.list_agent_workflows(organisation_id=organisation.id)


@router.post("", status_code=200)
def create_agent_workflow(agent_workflow: AgentWorkflowIn,
                          organisation=Depends(get_user_organisation),
                          Authorize: AuthJWT = Depends(check_auth)):
    return AgentWorkflowHelper.create_agent_workflow(name=agent_workflow.name,
                                                     description=agent_workflow.description,
                                                     organisation_id=organisation.id)


@router.get("/{agent_workflow_id}", status_code=200)
def get_agent_workflow(agent_workflow_id: int,
                       Authorize: AuthJWT = Depends(check_auth)):
    return AgentWorkflowHelper.get_agent_workflow(agent_workflow_id=agent_workflow_id)


@router.post("/code_yaml/{agent_workflow_id}", status_code=200)
def add_or_update_agent_workflow_code(agent_workflow_id: int, agent_workflow: AgentWorkflowIn,
                                      organisation=Depends(get_user_organisation),
                                      Authorize: AuthJWT = Depends(check_auth)):
    return AgentWorkflowHelper.add_or_update_agent_workflow_code(agent_workflow_id=agent_workflow_id,
                                                                 agent_workflow_code_yaml=agent_workflow.code_yaml,
                                                                 organisation_id=organisation.id)