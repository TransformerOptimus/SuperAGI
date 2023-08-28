from pydantic import BaseModel


class ToolExecutorResponse(BaseModel):
    status: str
    result: str = None
    retry: bool = False
    is_permission_required: bool = False
    permission_id: int = None


class TaskExecutorResponse(BaseModel):
    status: str
    retry: bool


class WebActionExecutorResponse(BaseModel):
    action: str
    action_reference_element: int
    action_reference_param: str
    status: str
    thoughts: str
