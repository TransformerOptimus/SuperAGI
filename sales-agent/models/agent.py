from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from models.database import Base


class SalesAgent(Base):
    """Sales Agent model"""
    __tablename__ = 'sales_agents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    goals = Column(JSON)  # List of goals
    instructions = Column(Text)
    constraints = Column(JSON)  # List of constraints
    tools = Column(JSON)  # List of enabled tool names
    model = Column(String(100), default='gpt-4')
    max_iterations = Column(Integer, default=25)
    iteration_interval = Column(Integer, default=300)  # seconds
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'goals': self.goals,
            'instructions': self.instructions,
            'constraints': self.constraints,
            'tools': self.tools,
            'model': self.model,
            'max_iterations': self.max_iterations,
            'iteration_interval': self.iteration_interval,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AgentExecution(Base):
    """Agent Execution model - represents a single run of an agent"""
    __tablename__ = 'agent_executions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, nullable=False)
    name = Column(String(255))
    status = Column(String(50), default='CREATED')  # CREATED, RUNNING, PAUSED, COMPLETED, FAILED
    current_step = Column(Integer, default=0)
    num_iterations = Column(Integer, default=0)
    num_tokens = Column(Integer, default=0)
    leads_processed = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status,
            'current_step': self.current_step,
            'num_iterations': self.num_iterations,
            'num_tokens': self.num_tokens,
            'leads_processed': self.leads_processed,
            'emails_sent': self.emails_sent,
            'responses_received': self.responses_received,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ExecutionLog(Base):
    """Execution logs - stores conversation history and tool outputs"""
    __tablename__ = 'execution_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, nullable=False)
    step = Column(Integer)
    role = Column(String(50))  # system, user, assistant, tool
    tool_name = Column(String(100))
    content = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'step': self.step,
            'role': self.role,
            'tool_name': self.tool_name,
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Lead(Base):
    """Lead model - stores prospect information"""
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), nullable=False)
    company = Column(String(255))
    title = Column(String(255))
    linkedin_url = Column(String(500))
    phone = Column(String(50))
    location = Column(String(255))
    company_domain = Column(String(255))
    company_size = Column(String(50))
    industry = Column(String(100))
    status = Column(String(50), default='NEW')  # NEW, CONTACTED, RESPONDED, QUALIFIED, DISQUALIFIED
    score = Column(Integer)
    research_data = Column(JSON)  # Company research findings
    email_sent = Column(Boolean, default=False)
    email_opened = Column(Boolean, default=False)
    email_replied = Column(Boolean, default=False)
    last_contacted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'company': self.company,
            'title': self.title,
            'linkedin_url': self.linkedin_url,
            'phone': self.phone,
            'location': self.location,
            'company_domain': self.company_domain,
            'company_size': self.company_size,
            'industry': self.industry,
            'status': self.status,
            'score': self.score,
            'research_data': self.research_data,
            'email_sent': self.email_sent,
            'email_opened': self.email_opened,
            'email_replied': self.email_replied,
            'last_contacted_at': self.last_contacted_at.isoformat() if self.last_contacted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
