from typing import List, Optional
from pydantic import BaseModel

class AgentPublish(BaseModel):
    name: str
    description: str
    agent_template_id: int
    goal: Optional[List[str]]
    instruction: Optional[List[str]]
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
    knowledge: Optional[int]

    class Config:
        orm_mode = True