from pydantic import BaseModel
from typing import List

class AgentWithConfig(BaseModel):
    name: str
    project_id: int
    description: str
    goal: List[str]
    agent_type: str
    constraints: str
    tools: List[str]
    exit: str
    iteration_interval: int
    model: str
    permission_type: str
    LTM_DB:str