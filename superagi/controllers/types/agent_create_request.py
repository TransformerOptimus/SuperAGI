from typing import List, Optional

from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.models.agent_execution import AgentExecution


class AgentExecutionConfigRequest(BaseModel):
    AgentExecution: Optional[sqlalchemy_to_pydantic(AgentExecution, exclude=["id"])]
    goal: List[str]
    instruction: List[str]
