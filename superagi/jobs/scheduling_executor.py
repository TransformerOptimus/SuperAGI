import importlib
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

import superagi.worker
from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution

from superagi.models.db import connect_db


engine = connect_db()
Session = sessionmaker(bind=engine)

class ScheduledAgentExecutor:

    @classmethod
    def execute_scheduled_agent(self, agent_id: int, name: str):

        session = Session()
        agent = session.query(Agent).get(agent_id)

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        start_step_id = AgentWorkflow.fetch_trigger_step_id(session, agent.agent_workflow_id)
        db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                            agent_id=agent_id, name=name, num_of_calls=0,
                                            num_of_tokens=0,
                                            current_step_id=start_step_id)
        session.add(db_agent_execution)
        session.commit()

        if db_agent_execution.status == "RUNNING":
            superagi.worker.execute_agent.delay(db_agent_execution.id, datetime.now())


        session.close()