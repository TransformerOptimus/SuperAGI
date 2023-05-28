import json

from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.agent_execution import AgentExecution
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(AgentExecutionFeed), status_code=201)
def create_agent_execution_feed(agent_execution_feed: sqlalchemy_to_pydantic(AgentExecutionFeed, exclude=["id"]),
                                Authorize: AuthJWT = Depends()):
    agent_execution = db.session.query(AgentExecution).get(agent_execution_feed.agent_execution_id)

    if not agent_execution:
        raise HTTPException(status_code=404, detail="Agent Execution not found")

    db_agent_execution_feed = AgentExecutionFeed(agent_execution_id=agent_execution_feed.agent_execution_id,
                                                 feed=agent_execution_feed.feed, type=agent_execution_feed.type)
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

    db_agent_execution_feed.type = agent_execution_feed.type
    db_agent_execution_feed.feed = agent_execution_feed.feed

    db.session.commit()
    return db_agent_execution_feed


@router.get("/get/execution/{agent_execution_id}")
def get_agent_execution_feed(agent_execution_id: int, Authorize: AuthJWT = Depends()):
    feeds = db.session.query(AgentExecutionFeed).filter_by(agent_execution_id=agent_execution_id).all()
    # parse json
    final_feeds = []
    for feed in feeds:
        final_feeds.append(parse_feed(feed))
    return final_feeds


def parse_feed(feed):
    if feed.role == "assistant":
        try:
            parsed = json.loads(feed.feed, strict=False)
            format_prefix_yellow = "\033[93m\033[1m"
            format_suffix_yellow = "\033[0m\033[0m"
            format_prefix_green = "\033[92m\033[1m"
            format_suffix_green = "\033[0m\033[0m"
            final_output = format_prefix_yellow + "Thoughts: " + format_suffix_yellow + parsed["thoughts"][
                "reasoning"] + "<br>"
            final_output += format_prefix_yellow + "Plan: " + format_suffix_yellow + parsed["thoughts"]["plan"] + "<br>"
            final_output += format_prefix_yellow + "Criticism: " + format_suffix_yellow + parsed["thoughts"][
                "criticism"] + "<br>"
            final_output += format_prefix_green + "Action : " + format_suffix_green + "<br>"
            final_output += format_prefix_yellow + "Tool: " + format_suffix_yellow + parsed["command"]["name"] + "<br>"

            return {"role": "assistant", "feed": final_output}
        except Exception:
            return feed
    if feed.role == "assistant":
        return feed

    return feed
