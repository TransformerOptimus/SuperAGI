from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db

from superagi.helper.auth import check_auth
from superagi.models.agent_execution_config import AgentExecutionConfiguration

router = APIRouter()


@router.get("/details/{agent_execution_id}")
def get_agent_execution_configuration(agent_execution_id: int,
                                      Authorize: AuthJWT = Depends(check_auth)):
    """
    Get the agent execution configuration using the agent execution ID.

    Args:
        agent_execution_id (int): Identifier of the agent.
        Authorize (AuthJWT, optional): Authorization dependency. Defaults to Depends(check_auth).

    Returns:
        dict: Agent Execution configuration including its details.

    Raises:
        HTTPException (status_code=404): If the agent is not found.
    """

    agent_execution_config = db.session.query(AgentExecutionConfiguration).filter(
        AgentExecutionConfiguration.agent_execution_id == agent_execution_id
    ).all()
    if not agent_execution_config:
        raise HTTPException(status_code=404, detail="Agent Execution Configuration not found")
    response = {result.key: eval(result.value) for result in agent_execution_config}

    return response
