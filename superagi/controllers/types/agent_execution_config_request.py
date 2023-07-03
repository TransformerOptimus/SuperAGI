from pydantic import BaseModel
from typing import List


class AgentExecutionConfigRequest(BaseModel):
    goal: List[str]
    instruction: List[str]
