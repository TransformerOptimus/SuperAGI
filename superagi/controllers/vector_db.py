from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent import Agent
from superagi.models.agent_template import AgentTemplate
from superagi.models.agent_template_config import AgentTemplateConfig
from superagi.models.project import Project
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.types.agent_with_config import AgentWithConfig
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.tool import Tool
from jsonmerge import merge
from superagi.worker import execute_agent
from datetime import datetime
import json
from sqlalchemy import func
from superagi.helper.auth import check_auth, get_user_organisation

router = APIRouter()

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

    marketplace_vector_dbs = Vectordb.fetch_marketplace_list(page=page)
    #marketplace_vector_dbs_with_install = Vectordb.get_vector_db_installed_details(db.session, marketplace_vector_dbs,
    #                                                                          organisation)
    return marketplace_vector_dbs

#For internal use
@router.get("/marketplace/list/{page}")
def get_marketplace_vectordb(
        page: int = 0,
):
    """
    Get marketplace vectordbs.

    Args:
        page (int): The page number for pagination.

    Returns:
        list: A list of vectordbs.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    page_size = 30

    # Apply search filter if provided
    query = db.session.query(Vectordb).filter(Vectordb.organisation_id == organisation_id)

    # Paginate the results
    vector_dbs = query.offset(page * page_size).limit(page_size).all()

    return vector_dbs
