import datetime
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class AgentRunIn(BaseModel):
    status: Optional[str]
    name: Optional[str]
    agent_id: Optional[int]
    last_execution_time: Optional[datetime]
    num_of_calls: Optional[int]
    num_of_tokens: Optional[int]
    current_step_id: Optional[int]
    permission_id: Optional[int]
    goal: Optional[List[str]]
    instruction: Optional[List[str]]
    agent_workflow: str
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