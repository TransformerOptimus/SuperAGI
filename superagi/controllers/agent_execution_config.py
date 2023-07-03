
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic.fields import List
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from superagi.helper.auth import check_auth
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.controllers.types.agent_create_request import AgentExecutionConfigRequest


router = APIRouter()


# @router.put("/update", response_model=AgentExecutionConfigRequest)
# def update_agent_execution_config(agent_execution_configs: AgentExecutionConfigRequest,
#                  Authorize: AuthJWT = Depends(check_auth)):
#     # db_agent_execution_config = db.session.query(AgentExecutionConfiguration).filter(
#     #     AgentExecutionConfiguration.key == agent_execution_config.key,
#     #     AgentExecutionConfiguration.agent_id == agent_execution_config.agent_id).first()
#     # if not db_agent_execution_config:
#     #     raise HTTPException(status_code=404, detail="Agent Configuration not found")
#     #
#     # db_agent_execution_config.key = agent_execution_config.key
#     # if isinstance(agent_execution_config.value, list):
#     #     db_agent_execution_config.value = str(agent_execution_config.value)
#     # else:
#     #     db_agent_execution_config.value = agent_execution_config.value
#     # db.session.commit()
#     # db.session.flush()
#     # return db_agent_execution_config
#     execution = db.session.query(AgentExecutionConfiguration).filter(AgentExecutionConfiguration.id == agent_execution_configs.execution_id).first()
#     if execution is None:
#         raise HTTPException(status_code=404,detail='Execution not found')
#     AgentExecutionConfiguration.add_or_update_agent_execution_config(session=db.session, execution=execution,
#                                                                      agent_execution_configs=agent_execution_configs)


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

    keys_to_fetch = ["goal", "instruction"]
    results = db.session.query(AgentExecutionConfiguration).filter(AgentExecutionConfiguration.key.in_(keys_to_fetch),
                                                                   AgentExecutionConfiguration.agent_execution_id == agent_execution_id).all()
    response = {result.key: result.value for result in results}

    return response
