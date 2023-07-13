from pydantic import BaseModel
from typing import List, Optional


class AgentConfigInput(BaseModel):
    name: str
    project_id: int
    description: str
    goal: List[str]
    instruction: List[str]
    agent_type: str
    constraints: List[str]
    toolkits: List[int]
    tools: List[int]
    exit: str
    iteration_interval: int
    model: str
    permission_type: str
    LTM_DB: str
    max_iterations: int
    user_timezone: Optional[str]
