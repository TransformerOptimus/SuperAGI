from fastapi import APIRouter
from fastapi import Depends
from fastapi_sqlalchemy import db

from superagi.helper.auth import get_user_organisation
from superagi.models.agent_workflow import AgentWorkflow

router = APIRouter()


@router.get("/list", status_code=201)
def list_workflows(organisation=Depends(get_user_organisation)):
    """List agent workflows"""
    workflows = db.session.query(AgentWorkflow).all()

    output_json = []
    for workflow in workflows:
        output_json.append(workflow.to_dict())
    return output_json
