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
