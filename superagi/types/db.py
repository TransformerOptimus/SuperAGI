from datetime import datetime

from pydantic.main import BaseModel


class Agent(BaseModel):
    name: str
    project_id: int
    description: str

    class Config:
        orm_mode = True


class AgentConfiguration(BaseModel):
    id: int
    agent_id: int
    key: str
    value: str

    class Config:
        orm_mode = True


class AgentExecution(BaseModel):
    id: int
    status: str
    name: str
    agent_id: int
    last_execution_time: datetime
    num_of_calls: int
    num_of_tokens: int
    current_step_id: int
    permission_id: int

    class Config:
        orm_mode = True


class AgentExecutionFeed(BaseModel):
    id: int
    agent_execution_id: int
    agent_id: int
    feed: str
    role: str
    extra_info: str

    class Config:
        orm_mode = True


class AgentExecutionPermission(BaseModel):
    id: int
    agent_execution_id: int
    agent_id: int
    status: str
    tool_name: str
    user_feedback: str
    assistant_reply: str

    class Config:
        orm_mode = True


class AgentTemplate(BaseModel):
    id: int
    organisation_id: int
    agent_workflow_id: int
    name: str
    description: str
    marketplace_template_id: int

    class Config:
        orm_mode = True


class AgentTemplateConfig(BaseModel):
    id: int
    agent_template_id: int
    key: str
    value: str

    class Config:
        orm_mode = True


class AgentWorkflow(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class AgentWorkflowStep(BaseModel):
    id: int
    agent_workflow_id: int
    unique_id: str
    prompt: str
    variables: str
    output_type: str
    step_type: str
    next_step_id: int
    history_enabled: bool
    completion_prompt: str

    class Config:
        orm_mode = True


class Budget(BaseModel):
    id: int
    budget: float
    cycle: str

    class Config:
        orm_mode = True


class Configuration(BaseModel):
    id: int
    organisation_id: int
    key: str
    value: str

    class Config:
        orm_mode = True


class Organisation(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class Project(BaseModel):
    id: int
    name: str
    organisation_id: int
    description: str

    class Config:
        orm_mode = True


class Resource(BaseModel):
    id: int
    name: str
    storage_type: str
    path: str
    size: int
    type: str
    channel: str
    agent_id: int

    class Config:
        orm_mode = True


class Tool(BaseModel):
    id: int
    name: str
    folder_name: str
    class_name: str
    file_name: str

    class Config:
        orm_mode = True


class ToolConfig(BaseModel):
    id: int
    name: str
    key: str
    value: str
    agent_id: int

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    organisation_id: int

    class Config:
        orm_mode = True

