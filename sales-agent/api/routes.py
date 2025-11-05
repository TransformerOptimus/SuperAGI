from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models import get_db, SalesAgent, AgentExecution, ExecutionLog, Lead
from api.schemas import (
    AgentCreate, AgentResponse, AgentUpdate,
    ExecutionCreate, ExecutionResponse,
    LeadResponse, LogResponse
)
from jobs.tasks import execute_agent_task


router = APIRouter()


# ==================== Agent Endpoints ====================

@router.post("/agents", response_model=AgentResponse, status_code=201)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """
    Create a new sales agent

    Creates a sales agent with goals, tools, and configuration.
    """
    db_agent = SalesAgent(
        name=agent.name,
        description=agent.description,
        goals=agent.goals,
        instructions=agent.instructions,
        constraints=agent.constraints,
        tools=agent.tools,
        model=agent.model,
        max_iterations=agent.max_iterations,
        iteration_interval=agent.iteration_interval
    )

    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)

    return db_agent.to_dict()


@router.get("/agents", response_model=List[AgentResponse])
def list_agents(
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """List all sales agents"""
    query = db.query(SalesAgent)

    if is_active is not None:
        query = query.filter(SalesAgent.is_active == is_active)

    agents = query.order_by(SalesAgent.created_at.desc()).all()
    return [agent.to_dict() for agent in agents]


@router.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get agent details"""
    agent = db.query(SalesAgent).filter(SalesAgent.id == agent_id).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.to_dict()


@router.put("/agents/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update agent configuration"""
    agent = db.query(SalesAgent).filter(SalesAgent.id == agent_id).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Update fields
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)

    return agent.to_dict()


@router.delete("/agents/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Deactivate an agent"""
    agent = db.query(SalesAgent).filter(SalesAgent.id == agent_id).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.is_active = False
    db.commit()

    return {"message": "Agent deactivated successfully"}


# ==================== Execution Endpoints ====================

@router.post("/executions", response_model=ExecutionResponse, status_code=201)
def create_execution(execution: ExecutionCreate, db: Session = Depends(get_db)):
    """
    Start a new agent execution

    Creates and queues an execution run for the specified agent.
    """
    # Verify agent exists
    agent = db.query(SalesAgent).filter(SalesAgent.id == execution.agent_id).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if not agent.is_active:
        raise HTTPException(status_code=400, detail="Agent is not active")

    # Create execution
    db_execution = AgentExecution(
        agent_id=execution.agent_id,
        name=execution.name or f"{agent.name} - {datetime.utcnow().isoformat()}",
        status="CREATED"
    )

    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)

    # Queue background task
    execute_agent_task.delay(db_execution.id)

    return db_execution.to_dict()


@router.get("/executions", response_model=List[ExecutionResponse])
def list_executions(
    agent_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """List agent executions"""
    query = db.query(AgentExecution)

    if agent_id:
        query = query.filter(AgentExecution.agent_id == agent_id)

    if status:
        query = query.filter(AgentExecution.status == status)

    executions = query.order_by(AgentExecution.created_at.desc()).all()
    return [execution.to_dict() for execution in executions]


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: int, db: Session = Depends(get_db)):
    """Get execution details"""
    execution = db.query(AgentExecution).filter(
        AgentExecution.id == execution_id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution.to_dict()


@router.post("/executions/{execution_id}/pause")
def pause_execution(execution_id: int, db: Session = Depends(get_db)):
    """Pause a running execution"""
    execution = db.query(AgentExecution).filter(
        AgentExecution.id == execution_id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.status != "RUNNING":
        raise HTTPException(status_code=400, detail="Execution is not running")

    execution.status = "PAUSED"
    db.commit()

    return {"message": "Execution paused"}


@router.post("/executions/{execution_id}/resume")
def resume_execution(execution_id: int, db: Session = Depends(get_db)):
    """Resume a paused execution"""
    execution = db.query(AgentExecution).filter(
        AgentExecution.id == execution_id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.status != "PAUSED":
        raise HTTPException(status_code=400, detail="Execution is not paused")

    execution.status = "RUNNING"
    db.commit()

    # Re-queue task
    execute_agent_task.delay(execution_id)

    return {"message": "Execution resumed"}


# ==================== Logs Endpoints ====================

@router.get("/executions/{execution_id}/logs", response_model=List[LogResponse])
def get_execution_logs(
    execution_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get execution logs and conversation history"""
    logs = db.query(ExecutionLog).filter(
        ExecutionLog.execution_id == execution_id
    ).order_by(ExecutionLog.created_at.asc()).limit(limit).all()

    return [log.to_dict() for log in logs]


# ==================== Leads Endpoints ====================

@router.get("/executions/{execution_id}/leads", response_model=List[LeadResponse])
def get_execution_leads(execution_id: int, db: Session = Depends(get_db)):
    """Get leads for an execution"""
    leads = db.query(Lead).filter(
        Lead.execution_id == execution_id
    ).order_by(Lead.created_at.desc()).all()

    return [lead.to_dict() for lead in leads]


@router.get("/leads", response_model=List[LeadResponse])
def list_leads(
    status: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all leads"""
    query = db.query(Lead)

    if status:
        query = query.filter(Lead.status == status)

    leads = query.order_by(Lead.created_at.desc()).limit(limit).all()
    return [lead.to_dict() for lead in leads]


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get lead details"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead.to_dict()


# ==================== Stats Endpoints ====================

@router.get("/stats/overview")
def get_stats_overview(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_agents = db.query(SalesAgent).filter(SalesAgent.is_active == True).count()
    total_executions = db.query(AgentExecution).count()
    total_leads = db.query(Lead).count()
    emails_sent = db.query(AgentExecution).with_entities(
        db.func.sum(AgentExecution.emails_sent)
    ).scalar() or 0
    responses = db.query(AgentExecution).with_entities(
        db.func.sum(AgentExecution.responses_received)
    ).scalar() or 0

    return {
        "total_agents": total_agents,
        "total_executions": total_executions,
        "total_leads": total_leads,
        "emails_sent": emails_sent,
        "responses_received": responses,
        "response_rate": (responses / emails_sent * 100) if emails_sent > 0 else 0
    }
