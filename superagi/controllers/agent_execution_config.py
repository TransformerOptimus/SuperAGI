from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from superagi.helper.auth import check_auth
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.controllers.types.agent_execution_config_request import AgentExecutionConfigRequest
router = APIRouter()


@router.put("/update", response_model=sqlalchemy_to_pydantic(AgentExecutionConfiguration))
def update_agent(agent_execution_config: AgentExecutionConfigRequest,
                 Authorize: AuthJWT = Depends(check_auth)):
    """
        Update a particular agent execution configuration value for the given agent_id and agent_config key.

        Args:
            agent_execution_config (AgentExecutionConfiguration): The updated agent configuration data.

        Returns:
            AgentConfiguration: The updated agent execution configuration.

        Raises:
            HTTPException (Status Code=404): If the agent configuration is not found.
    """

    db_agent_execution_config = db.session.query(AgentExecutionConfiguration).filter(
        AgentExecutionConfiguration.key == agent_execution_config.key,
        AgentExecutionConfiguration.agent_id == agent_execution_config.agent_id).first()
    if not db_agent_execution_config:
        raise HTTPException(status_code=404, detail="Agent Configuration not found")

    db_agent_execution_config.key = agent_execution_config.key
    if isinstance(agent_execution_config.value, list):
        db_agent_execution_config.value = str(agent_execution_config.value)
    else:
        db_agent_execution_config.value = agent_execution_config.value
    db.session.commit()
    db.session.flush()
    return db_agent_execution_config


@router.get("/details/{agent_execution_id}")
def get_agent_configuration(agent_execution_id: int,
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

    keys_to_fetch = ["goal", "instruction"]
    results = db.session.query(AgentExecutionConfiguration).filter(AgentExecutionConfiguration.key.in_(keys_to_fetch),
                                                                   AgentExecutionConfiguration.agent_execution_id == agent_execution_id).all()
    response = {result.key: result.value for result in results}

    return response
