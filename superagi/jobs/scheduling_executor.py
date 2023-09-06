import ast
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from superagi.models.tool import Tool

from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.worker import execute_agent
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.apm.event_handler import EventHandler
from superagi.models.knowledges import Knowledges
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

        db_agent_execution = AgentExecution(status="CREATED", last_execution_time=datetime.now(),
                                            agent_id=agent_id, name=name, num_of_calls=0,
                                            num_of_tokens=0,
                                            current_agent_step_id=start_step.id,
                                            iteration_workflow_step_id=iteration_step_id)

        session.add(db_agent_execution)
        session.commit()

        #update status from CREATED to RUNNING
        db_agent_execution.status = "RUNNING"
        session.commit()

        agent_execution_id = db_agent_execution.id
        agent_configurations = session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id).all()
        for agent_config in agent_configurations:
            agent_execution_config = AgentExecutionConfiguration(agent_execution_id=agent_execution_id, key=agent_config.key, value=agent_config.value)
            session.add(agent_execution_config)
        organisation = agent.get_agent_organisation(session)
        model = session.query(AgentConfiguration.value).filter(AgentConfiguration.agent_id == agent_id).filter(AgentConfiguration.key == 'model').first()[0]

        EventHandler(session=session).create_event('run_created',
                                                   {'agent_execution_id': db_agent_execution.id,
                                                    'agent_execution_name':db_agent_execution.name},
                                                    agent_id,
                                                    organisation.id if organisation else 0)
        agent_execution_knowledge = AgentConfiguration.get_agent_config_by_key_and_agent_id(session= session, key= 'knowledge', agent_id= agent_id)
        if agent_execution_knowledge and agent_execution_knowledge.value != 'None':
            knowledge_name = Knowledges.get_knowledge_from_id(session, int(agent_execution_knowledge.value)).name
            if knowledge_name is not None:
                EventHandler(session=session).create_event('knowledge_picked',
                                                        {'knowledge_name': knowledge_name,
                                                         'agent_execution_id': db_agent_execution.id},
                                                        agent_id,
                                                        organisation.id if organisation else 0)
        session.commit()

        if db_agent_execution.status == "RUNNING":
            execute_agent.delay(db_agent_execution.id, datetime.now())

        session.close()