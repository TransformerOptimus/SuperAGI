from pydantic import BaseModel


class WebInteractorActionRequest(BaseModel):
    dom_content: str
    agent_execution_id: int
    last_action_status: bool

