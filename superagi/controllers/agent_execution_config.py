import ast

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from typing import Optional, Union

from superagi.helper.auth import check_auth
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration

router = APIRouter()


@router.get("/details/agent/{agent_id}/agent_execution/{agent_execution_id}")
def get_agent_execution_configuration(agent_id : int,
                                      agent_execution_id: Optional[Union[int, None]] = None,
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
    if agent_execution_id > 0:
        agent_execution_config = db.session.query(AgentExecutionConfiguration).filter(
            AgentExecutionConfiguration.agent_execution_id == agent_execution_id
        ).all()
        if agent_execution_config:
            return {result.key: eval(result.value) for result in agent_execution_config}

        agent_execution = db.session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        if not agent_execution:
            raise HTTPException(status_code=404, detail="Agent Configuration not found")
    keys_to_fetch = ["goal", "instruction"]
    agent_configuration = db.session.query(AgentConfiguration).filter(AgentConfiguration.key.in_(keys_to_fetch),
                                                                      AgentConfiguration.agent_id == agent_id).all()

    return {result.key: ast.literal_eval(result.value) for result in agent_configuration}
