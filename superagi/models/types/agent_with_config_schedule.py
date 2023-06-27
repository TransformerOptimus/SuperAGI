from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AgentWithConfigSchedule(BaseModel):
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
    memory_window: int
    max_iterations: int
    agent_id: Optional[int]
    start_time: datetime
    recurrence_interval: Optional[str] = None
    expiry_date: Optional[datetime] = None
    expiry_runs: Optional[int] = -1