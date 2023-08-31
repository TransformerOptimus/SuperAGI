from pydantic import BaseModel


class WebInteractorNextActionRequest(BaseModel):
    dom_content: str
    agent_execution_id: int
    last_action_status: str
    last_action: str
    page_url: str
