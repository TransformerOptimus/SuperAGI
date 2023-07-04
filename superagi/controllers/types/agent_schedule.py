from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AgentScheduleInput(BaseModel):
    agent_id: Optional[int]
    start_time: datetime
    recurrence_interval: Optional[str] = None
    expiry_date: Optional[datetime] = None
    expiry_runs: Optional[int] = -1
