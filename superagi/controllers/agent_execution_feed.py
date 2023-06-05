import json

from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.agent_execution import AgentExecution
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy.sql import desc,asc


router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentExecutionFeed), status_code=201)
def create_agent_execution_feed(agent_execution_feed: sqlalchemy_to_pydantic(AgentExecutionFeed, exclude=["id"]),
                                Authorize: AuthJWT = Depends()):
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
def get_agent_execution_feed(agent_execution_feed_id: int, Authorize: AuthJWT = Depends()):
    db_agent_execution_feed = db.session.query(AgentExecutionFeed).filter(
        AgentExecutionFeed.id == agent_execution_feed_id).first()
    if not db_agent_execution_feed:
        raise HTTPException(status_code=404, detail="agent_execution_feed not found")
    return db_agent_execution_feed


@router.put("/update/{agent_execution_feed_id}", response_model=sqlalchemy_to_pydantic(AgentExecutionFeed))
def update_agent_execution_feed(agent_execution_feed_id: int,
                                agent_execution_feed: sqlalchemy_to_pydantic(AgentExecutionFeed, exclude=["id"])):
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
def get_agent_execution_feed(agent_execution_id: int, Authorize: AuthJWT = Depends()):
    feeds = db.session.query(AgentExecutionFeed).filter_by(agent_execution_id=agent_execution_id).order_by(asc(AgentExecutionFeed.created_at)).all()
    # parse json
    final_feeds = []
    for feed in feeds:
        final_feeds.append(parse_feed(feed))
    return final_feeds


def parse_feed(feed):
    if feed.role == "assistant":
        try:
            parsed = json.loads(feed.feed, strict=False)
            final_output = "Thoughts: " + parsed["thoughts"][
                "reasoning"] + "\n"
            final_output += "Plan: " + parsed["thoughts"]["plan"] + "\n"
            final_output += "Criticism: " + parsed["thoughts"][
                "criticism"] + "\n"
            final_output += "Tool: " + parsed["command"]["name"] + "\n"

            return {"role": "assistant", "feed": final_output, "updated_at":feed.updated_at}
        except Exception:
            return feed
    if feed.role == "assistant":
        return feed

    return feed
