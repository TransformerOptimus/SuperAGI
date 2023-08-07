from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.worker import execute_agent
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.apm.event_handler import EventHandler

from superagi.models.db import connect_db


engine = connect_db()
Session = sessionmaker(bind=engine)

class ScheduledAgentExecutor:

    def execute_scheduled_agent(self, agent_id: int, name: str):
        """
        Performs the execution of scheduled agents

        Args:
            agent_id: Identifier of the agent
            name: Name of the agent
        """
        session = Session()
        agent = session.query(Agent).get(agent_id)

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")



        start_step = AgentWorkflow.fetch_trigger_step_id(session, agent.agent_workflow_id)
        iteration_step_id = IterationWorkflow.fetch_trigger_step_id(session,
                                                                    start_step.action_reference_id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1

        db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                            agent_id=agent_id, name=name, num_of_calls=0,
                                            num_of_tokens=0,
                                            current_agent_step_id=start_step.id,
                                            iteration_workflow_step_id=iteration_step_id)

        session.add(db_agent_execution)
        session.commit()

        goal_value = session.query(AgentConfiguration.value).filter(AgentConfiguration.agent_id == agent_id).filter(AgentConfiguration.key == 'goal').first()[0]
        instruction_value = session.query(AgentConfiguration.value).filter(AgentConfiguration.agent_id == agent_id).filter(AgentConfiguration.key == 'instruction').first()[0]

        agent_execution_configs = {
            "goal": goal_value,
            "instruction": instruction_value
        }


        AgentExecutionConfiguration.add_or_update_agent_execution_config(session= session, execution=db_agent_execution,agent_execution_configs=agent_execution_configs)


        organisation = agent.get_agent_organisation(session)
        model = session.query(AgentConfiguration.value).filter(AgentConfiguration.agent_id == agent_id).filter(AgentConfiguration.key == 'model').first()[0]
        EventHandler(session=session).create_event('run_created', {'agent_execution_id': db_agent_execution.id,'agent_execution_name':db_agent_execution.name}, agent_id, organisation.id if organisation else 0),

        session.commit()

        if db_agent_execution.status == "RUNNING":
            execute_agent.delay(db_agent_execution.id, datetime.now())

        session.close()