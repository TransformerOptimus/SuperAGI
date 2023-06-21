from datetime import datetime

from pydantic.main import BaseModel


class DBModel(BaseModel):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AgentOut(DBModel):
    id: int
    name: str
    project_id: int
    description: str

    class Config:
        orm_mode = True


class AgentIn(BaseModel):
    name: str
    project_id: int
    description: str

    class Config:
        orm_mode = True


class AgentConfigurationOut(DBModel):
    id: int
    agent_id: int
    key: str
    value: str

    class Config:
        orm_mode = True


class AgentConfigurationIn(BaseModel):
    agent_id: int
    key: str
    value: str

    class Config:
        orm_mode = True


class AgentExecutionOut(DBModel):
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


class AgentExecutionIn(BaseModel):
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

class AgentExecutionFeedOut(DBModel):
    id: int
    agent_execution_id: int
    agent_id: int
    feed: str
    role: str
    extra_info: str

    class Config:
        orm_mode = True


class AgentExecutionFeedIn(BaseModel):
    id: int
    agent_execution_id: int
    agent_id: int
    feed: str
    role: str
    extra_info: str

    class Config:
        orm_mode = True


class AgentExecutionPermissionOut(DBModel):
    id: int
    agent_execution_id: int
    agent_id: int
    status: str
    tool_name: str
    user_feedback: str
    assistant_reply: str

    class Config:
        orm_mode = True


class AgentExecutionPermissionIn(BaseModel):
    agent_execution_id: int
    agent_id: int
    status: str
    tool_name: str
    user_feedback: str
    assistant_reply: str

    class Config:
        orm_mode = True


class AgentTemplateOut(DBModel):
    id: int
    organisation_id: int
    agent_workflow_id: int
    name: str
    description: str
    marketplace_template_id: int

    class Config:
        orm_mode = True


class AgentTemplateIn(BaseModel):
    organisation_id: int
    agent_workflow_id: int
    name: str
    description: str
    marketplace_template_id: int

    class Config:
        orm_mode = True


class AgentTemplateConfigOut(DBModel):
    id: int
    agent_template_id: int
    key: str
    value: str

    class Config:
        orm_mode = True


class AgentTemplateConfigIn(BaseModel):
    agent_template_id: int
    key: str
    value: str

    class Config:
        orm_mode = True


class AgentWorkflowOut(DBModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class AgentWorkflowIn(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class AgentWorkflowStepOut(DBModel):
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


class AgentWorkflowStepIn(BaseModel):
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

class BudgetOut(DBModel):
    id: int
    budget: float
    cycle: str

    class Config:
        orm_mode = True

class BudgetIn(BaseModel):
    budget: float
    cycle: str

    class Config:
        orm_mode = True



class ConfigurationOut(DBModel):
    id: int
    organisation_id: int
    key: str
    value: str

    class Config:
        orm_mode = True


class ConfigurationIn(BaseModel):
    id: int
    organisation_id: int
    key: str
    value: str

    class Config:
        orm_mode = True

class OrganisationOut(DBModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class OrganisationIn(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True

class ProjectOut(DBModel):
    id: int
    name: str
    organisation_id: int
    description: str

    class Config:
        orm_mode = True


class ProjectIn(BaseModel):
    name: str
    organisation_id: int
    description: str

    class Config:
        orm_mode = True

class ResourceOut(DBModel):
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

class ResourceIn(BaseModel):
    name: str
    storage_type: str
    path: str
    size: int
    type: str
    channel: str
    agent_id: int

    class Config:
        orm_mode = True


class ToolOut(DBModel):
    id: int
    name: str
    folder_name: str
    class_name: str
    file_name: str

    class Config:
        orm_mode = True


class ToolIn(BaseModel):
    name: str
    folder_name: str
    class_name: str
    file_name: str

    class Config:
        orm_mode = True


class ToolConfigOut(DBModel):
    id: int
    name: str
    key: str
    value: str
    agent_id: int

    class Config:
        orm_mode = True


class ToolConfigIn(BaseModel):
    name: str
    key: str
    value: str
    agent_id: int

    class Config:
        orm_mode = True


class UserOut(DBModel):
    id: int
    name: str
    email: str
    password: str
    organisation_id: int

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    name: str
    email: str
    password: str
    organisation_id: int

    class Config:
        orm_mode = True