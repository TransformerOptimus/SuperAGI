from pydantic import BaseModel
from typing import List


class AgentWithConfig(BaseModel):
    name: str
    project_id: int
    description: str
    goal: List[str]
    instruction: List[str]
    agent_type: str
    constraints: List[str]
    tools: List[int]
    exit: str
    iteration_interval: int
    model: str
    permission_type: str
    LTM_DB: str
    memory_window: int
    max_iterations: int
