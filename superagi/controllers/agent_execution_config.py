import ast
import json

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from typing import Optional, Union
from sqlalchemy import func, or_
from sqlalchemy import desc

from superagi.helper.auth import check_auth
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.tool import Tool
from superagi.models.knowledges import Knowledges


router = APIRouter()

@router.get("/details/agent_id/{agent_id}/agent_execution_id/{agent_execution_id}")
def get_agent_execution_configuration(agent_id : Union[int, None, str],
                                      agent_execution_id: Union[int, None, str],
                                      Authorize: AuthJWT = Depends(check_auth)):
   
    """
    Get the agent configuration using the agent ID and the agent execution ID.

    Args:
        agent_id (int): Identifier of the agent.
        agent_execution_id (int): Identifier of the agent execution.
        Authorize (AuthJWT, optional): Authorization dependency. Defaults to Depends(check_auth).

    Returns:
        dict: Agent configuration including its details.

    Raises:
        HTTPException (status_code=404): If the agent is not found or deleted.
        HTTPException (status_code=404): If the agent_id or the agent_execution_id is undefined.
    """

    # Check
    if isinstance(agent_id, str):
        raise HTTPException(status_code = 404, detail = "Agent Id undefined")
    if isinstance(agent_execution_id, str):
        raise HTTPException(status_code = 404, detail = "Agent Execution Id undefined")

    # Define the agent_config keys to fetch
    agent = db.session.query(Agent).filter(agent_id == Agent.id,or_(Agent.is_deleted == False)).first()
    if not agent:
        raise HTTPException(status_code = 404, detail = "Agent not found")
    
    #If the agent_execution_id received is -1 then the agent_execution_id is set as the most recent execution
    if agent_execution_id == -1:
        agent_execution = db.session.query(AgentExecution).filter(AgentExecution.agent_id == agent_id).order_by(desc(AgentExecution.created_at)).first()
        if agent_execution: agent_execution_id = agent_execution.id

    #Fetch agent id from agent execution id and check whether the agent_id received is correct or not.
    if agent_execution_id!=-1: 
        agent_execution_config = AgentExecution.get_agent_execution_from_id(db.session, agent_execution_id)
        if agent_execution_config is None:
            raise HTTPException(status_code = 404, detail = "Agent Execution not found")
        agent_id_from_execution_id = agent_execution_config.agent_id
        if agent_id != agent_id_from_execution_id:
            raise HTTPException(status_code = 404, detail = "Wrong agent id")

    # Query the AgentConfiguration table and the AgentExecuitonConfiguration table for all the keys
    results_agent = db.session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id).all()
    if agent_execution_id!=-1: results_agent_execution = db.session.query(AgentExecutionConfiguration).filter(AgentExecutionConfiguration.agent_execution_id == agent_execution_id).all()
    
    total_calls = db.session.query(func.sum(AgentExecution.num_of_calls)).filter(
        AgentExecution.agent_id == agent_id).scalar()
    total_tokens = db.session.query(func.sum(AgentExecution.num_of_tokens)).filter(
        AgentExecution.agent_id == agent_id).scalar()
    
    response = {}
    if agent_execution_id!=-1: 
        response = AgentExecutionConfiguration.build_agent_execution_config(db.session, agent, results_agent, results_agent_execution, total_calls, total_tokens)
    else: 
        response = AgentExecutionConfiguration.build_scheduled_agent_execution_config(db.session, agent, results_agent, total_calls, total_tokens)
        
    # Close the session
    db.session.close()

    return response