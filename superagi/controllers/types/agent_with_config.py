from pydantic import BaseModel
from typing import List, Optional
from superagi.controllers.types.agent_schedule import AgentScheduleInput

class AgentConfigInput(BaseModel):
    name: str
    project_id: int
    description: str
    goal: List[str]
    instruction: List[str]
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



class AgentConfigExtInput(BaseModel):
    name: str
    description: str
    project_id: Optional[int]
    goal: List[str]
    instruction: List[str]
    agent_workflow: str
    constraints: List[str]
    tools: List[dict]
    LTM_DB:Optional[str]
    exit: Optional[str]
    permission_type: Optional[str]
    iteration_interval: int
    model: str
    schedule: Optional[AgentScheduleInput]
    max_iterations: int
    user_timezone: Optional[str]
    knowledge: Optional[int]

class AgentConfigUpdateExtInput(BaseModel):
    name: Optional[str]
    description: Optional[str]
    project_id: Optional[int]
    goal: Optional[List[str]]
    instruction: Optional[List[str]]
    agent_workflow: Optional[str]
    constraints: Optional[List[str]]
    tools: Optional[List[dict]]
    LTM_DB:Optional[str]
    exit: Optional[str]
    permission_type: Optional[str]
    iteration_interval: Optional[int]
    model: Optional[str]
    schedule: Optional[AgentScheduleInput]
    max_iterations: Optional[int]
    user_timezone: Optional[str]
    knowledge: Optional[int]


