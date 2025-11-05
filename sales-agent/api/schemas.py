from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== Agent Schemas ====================

class AgentCreate(BaseModel):
    """Schema for creating a sales agent"""
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    goals: List[str] = Field(..., description="List of agent goals")
    instructions: str = Field(..., description="Agent instructions")
    constraints: List[str] = Field(default_factory=list, description="Agent constraints")
    tools: List[str] = Field(..., description="List of tool names to enable")
    model: str = Field(default="gpt-4", description="LLM model to use")
    max_iterations: int = Field(default=25, description="Maximum iterations")
    iteration_interval: int = Field(default=300, description="Seconds between iterations")


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    goals: Optional[List[str]] = None
    instructions: Optional[str] = None
    constraints: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    model: Optional[str] = None
    max_iterations: Optional[int] = None
    iteration_interval: Optional[int] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    """Schema for agent response"""
    id: int
    name: str
    description: Optional[str]
    goals: Optional[List[str]]
    instructions: Optional[str]
    constraints: Optional[List[str]]
    tools: Optional[List[str]]
    model: str
    max_iterations: int
    iteration_interval: int
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


# ==================== Execution Schemas ====================

class ExecutionCreate(BaseModel):
    """Schema for creating an execution"""
    agent_id: int = Field(..., description="Agent ID to execute")
    name: Optional[str] = Field(None, description="Execution name")


class ExecutionResponse(BaseModel):
    """Schema for execution response"""
    id: int
    agent_id: int
    name: Optional[str]
    status: str
    current_step: int
    num_iterations: int
    num_tokens: int
    leads_processed: int
    emails_sent: int
    responses_received: int
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


# ==================== Log Schemas ====================

class LogResponse(BaseModel):
    """Schema for execution log response"""
    id: int
    execution_id: int
    step: Optional[int]
    role: str
    tool_name: Optional[str]
    content: str
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[str]


# ==================== Lead Schemas ====================

class LeadResponse(BaseModel):
    """Schema for lead response"""
    id: int
    execution_id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    company: Optional[str]
    title: Optional[str]
    linkedin_url: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    company_domain: Optional[str]
    company_size: Optional[str]
    industry: Optional[str]
    status: str
    score: Optional[int]
    research_data: Optional[Dict[str, Any]]
    email_sent: bool
    email_opened: bool
    email_replied: bool
    last_contacted_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
