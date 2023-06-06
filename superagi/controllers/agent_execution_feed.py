import json

from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT

from superagi.agent.task_queue import TaskQueue
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.agent_execution import AgentExecution
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy.sql import desc,asc
from superagi.helper.auth import check_auth


router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentExecutionFeed), status_code=201)
def create_agent_execution_feed(agent_execution_feed: sqlalchemy_to_pydantic(AgentExecutionFeed, exclude=["id"]),
                                Authorize: AuthJWT = Depends(check_auth)):
    """Add a new agent execution feed"""

    agent_execution = db.session.query(AgentExecution).get(agent_execution_feed.agent_execution_id)

    if not agent_execution:
        raise HTTPException(status_code=404, detail="Agent Execution not found")

    db_agent_execution_feed = AgentExecutionFeed(agent_execution_id=agent_execution_feed.agent_execution_id,
                                                 feed=agent_execution_feed.feed, type=agent_execution_feed.type,
                                                 extra_info=agent_execution_feed.extra_info)
    db.session.add(db_agent_execution_feed)
    db.session.commit()
    return db_agent_execution_feed


@router.get("/get/{agent_execution_feed_id}", response_model=sqlalchemy_to_pydantic(AgentExecutionFeed))
def get_agent_execution_feed(agent_execution_feed_id: int,
                             Authorize: AuthJWT = Depends(check_auth)):
    """Get an agent execution feed by agent_execution feed id"""

    db_agent_execution_feed = db.session.query(AgentExecutionFeed).filter(
        AgentExecutionFeed.id == agent_execution_feed_id).first()
    if not db_agent_execution_feed:
        raise HTTPException(status_code=404, detail="agent_execution_feed not found")
    return db_agent_execution_feed


@router.put("/update/{agent_execution_feed_id}", response_model=sqlalchemy_to_pydantic(AgentExecutionFeed))
def update_agent_execution_feed(agent_execution_feed_id: int,
                                agent_execution_feed: sqlalchemy_to_pydantic(AgentExecutionFeed, exclude=["id"]),
                                Authorize: AuthJWT = Depends(check_auth)):
    """Update a particular agent_execution_feed_id"""

    db_agent_execution_feed = db.session.query(AgentExecutionFeed).filter(
        AgentExecutionFeed.id == agent_execution_feed_id).first()
    if not db_agent_execution_feed:
        raise HTTPException(status_code=404, detail="Agent Execution Feed not found")

    if agent_execution_feed.agent_execution_id:
        agent_execution = db.session.query(AgentExecution).get(agent_execution_feed.agent_execution_id)
        if not agent_execution:
            raise HTTPException(status_code=404, detail="Agent Execution not found")
        db_agent_execution_feed.agent_execution_id = agent_execution.id

    if agent_execution_feed.type is not None:
        db_agent_execution_feed.type = agent_execution_feed.type
    if agent_execution_feed.feed is not None:
        db_agent_execution_feed.feed = agent_execution_feed.feed
    # if agent_execution_feed.extra_info is not None:
    #     db_agent_execution_feed.extra_info = agent_execution_feed.extra_info

    db.session.commit()
    return db_agent_execution_feed


@router.get("/get/execution/{agent_execution_id}")
def get_agent_execution_feed(agent_execution_id: int,
                             Authorize: AuthJWT = Depends(check_auth)):
    """Get agent execution feed with other execution details"""

    agent_execution = db.session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    if agent_execution is None:
        raise HTTPException(status_code=400, detail="Agent Run not found!")
    feeds = db.session.query(AgentExecutionFeed).filter_by(agent_execution_id=agent_execution_id).order_by(asc(AgentExecutionFeed.created_at)).all()
    # # parse json
    final_feeds = []
    for feed in feeds:
        final_feeds.append(parse_feed(feed))
    return {
        "status": agent_execution.status,
        "feeds": final_feeds
    }

@router.get("/get/tasks/{agent_execution_id}")
def get_execution_tasks(agent_execution_id: int,
                             Authorize: AuthJWT = Depends(check_auth)):
    """Get agent execution feed with other execution details"""
    task_queue = TaskQueue(str(agent_execution_id))
    tasks = []
    for task in task_queue.get_tasks():
        tasks.append({"name": task})
    completed_tasks = []
    for task in reversed(task_queue.get_completed_tasks()):
        completed_tasks.append({"name": task['task']})

    return {
        "tasks": tasks,
        "completed_tasks": completed_tasks
    }

def parse_feed(feed):
    if feed.role == "assistant":
        try:
            parsed = json.loads(feed.feed, strict=False)

            final_output = ""
            if "reasoning" in parsed["thoughts"]:
                final_output = "Thoughts: " + parsed["thoughts"]["reasoning"] + "\n"
            if "plan" in parsed["thoughts"]:
                final_output += "Plan: " + parsed["thoughts"]["plan"] + "\n"
            if "criticism" in parsed["thoughts"]:
                final_output += "Criticism: " + parsed["thoughts"]["criticism"] + "\n"
            if "tool" in parsed:
                final_output += "Tool: " + parsed["tool"]["name"] + "\n"
            if "command" in parsed:
                final_output += "Tool: " + parsed["command"]["name"] + "\n"

            return {"role": "assistant", "feed": final_output, "updated_at": feed.updated_at}
        except Exception:
            return feed
    if feed.role == "system":
        return feed

    return feed
