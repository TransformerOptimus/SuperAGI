from pydantic import BaseModel
from superagi.controllers.types.agent_schedule import AgentScheduler
from superagi.controllers.types.agent_with_config import AgentWithConfig


class AgentWithConfigSchedule(BaseModel):
    agent: AgentWithConfig
    schedule: AgentScheduler