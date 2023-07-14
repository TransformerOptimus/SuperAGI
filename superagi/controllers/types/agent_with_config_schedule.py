from pydantic import BaseModel
from superagi.controllers.types.agent_schedule import AgentScheduleInput
from superagi.controllers.types.agent_with_config import AgentConfigInput


class AgentConfigSchedule(BaseModel):
    agent_config: AgentConfigInput
    schedule: AgentScheduleInput