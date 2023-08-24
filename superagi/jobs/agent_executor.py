from datetime import datetime, timedelta
from time import perf_counter

from sqlalchemy.orm import sessionmaker

import superagi.worker
from superagi.agent.agent_iteration_step_handler import AgentIterationStepHandler
from superagi.agent.agent_tool_step_handler import AgentToolStepHandler
from superagi.apm.event_handler import EventHandler
from superagi.lib.logger import logger
from superagi.llms.google_palm import GooglePalm
from superagi.llms.llm_model_factory import get_model
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.db import connect_db
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.types.model_source_types import ModelSourceType
from superagi.types.vector_store_types import VectorStoreType
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory

# from superagi.helper.tool_helper import get_tool_config_by_key

engine = connect_db()
Session = sessionmaker(bind=engine)


class AgentExecutor:

    def execute_next_step(self, agent_execution_id):
        t0_start = perf_counter()
        global engine
        # try:
        engine.dispose()
        session = Session()
        try:
            t1_start = perf_counter()
            agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            '''Avoiding running old agent executions'''
            if agent_execution and agent_execution.created_at < datetime.utcnow() - timedelta(days=1):
                logger.error("Older agent execution found, skipping execution")
                return
            t1_stop = perf_counter()
            logger.info("Time taken to get agent execution: " + str(t1_stop - t1_start))
            t1_start = perf_counter()
            agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
            agent_config = Agent.fetch_configuration(session, agent.id)
            if agent.is_deleted or (
                    agent_execution.status != "RUNNING" and agent_execution.status != "WAITING_FOR_PERMISSION"):
                logger.error(f"Agent execution stopped. {agent.id}: {agent_execution.status}")
                return
            t1_stop = perf_counter()
            logger.info("Time taken to get agent: 2" + str(t1_stop - t1_start))

            t1_start = perf_counter()
            organisation = Agent.find_org_by_agent_id(session, agent_id=agent.id)
            if self._check_for_max_iterations(session, organisation.id, agent_config, agent_execution_id):
                logger.error(f"Agent execution stopped. Max iteration exceeded. {agent.id}: {agent_execution.status}")
                return

            t1_stop = perf_counter()
            logger.info("Time taken to get organisation: 3" + str(t1_stop - t1_start))
            model_api_key = AgentConfiguration.get_model_api_key(session, agent_execution.agent_id, agent_config["model"])
            model_llm_source = ModelSourceType.get_model_source_from_model(agent_config["model"]).value
            t1_start = perf_counter()
            try:
                vector_store_type = VectorStoreType.get_vector_store_type(agent_config["LTM_DB"])
                memory = VectorFactory.get_vector_storage(vector_store_type, "super-agent-index1",
                                                          AgentExecutor.get_embedding(model_llm_source, model_api_key))
            except:
                logger.info("Unable to setup the pinecone connection...")
                memory = None

            t1_stop = perf_counter()
            logger.info("Time taken to get memory: 4 : " + str(t1_stop - t1_start))
            agent_workflow_step = session.query(AgentWorkflowStep).filter(
                AgentWorkflowStep.id == agent_execution.current_agent_step_id).first()
            t1_start = perf_counter()
            try:
                if agent_workflow_step.action_type == "TOOL":
                    tool_step_handler = AgentToolStepHandler(session,
                                                             llm=get_model(model=agent_config["model"], api_key=model_api_key)
                                                             , agent_id=agent.id, agent_execution_id=agent_execution_id,
                                                             memory=memory)
                    tool_step_handler.execute_step()
                elif agent_workflow_step.action_type == "ITERATION_WORKFLOW":
                    iteration_step_handler = AgentIterationStepHandler(session,
                                                                  llm=get_model(model=agent_config["model"],
                                                                                api_key=model_api_key)
                                                                       , agent_id=agent.id,
                                                                       agent_execution_id=agent_execution_id, memory=memory)
                    iteration_step_handler.execute_step()
            except Exception as e:
                logger.info("Exception in executing the step: {}".format(e))
                superagi.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=15)
                return
            t1_stop = perf_counter()
            logger.info("Time taken to execute step: iteration " + str(t1_stop - t1_start))

            agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            if agent_execution.status == "COMPLETED" or agent_execution.status == "WAITING_FOR_PERMISSION":
                logger.info("Agent Execution is completed or waiting for permission")
                session.close()
                return
            # superagi.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=0)
            superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())
        finally:
            t0_stop = perf_counter()
            logger.info("Time taken to execute agent: " + str(t0_stop - t0_start))
            session.close()
            engine.dispose()

    @classmethod
    def get_embedding(cls, model_source, model_api_key):
        if "OpenAi" in model_source:
            return OpenAiEmbedding(api_key=model_api_key)
        if "Google" in model_source:
            return GooglePalm(api_key=model_api_key)
        return None

    def _check_for_max_iterations(self, session, organisation_id, agent_config, agent_execution_id):
        db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        if agent_config["max_iterations"] <= db_agent_execution.num_of_calls:
            db_agent_execution.status = "ITERATION_LIMIT_EXCEEDED"

            EventHandler(session=session).create_event('run_iteration_limit_crossed',
                                                       {'agent_execution_id': db_agent_execution.id,
                                                        'name': db_agent_execution.name,
                                                        'tokens_consumed': db_agent_execution.num_of_tokens,
                                                        "calls": db_agent_execution.num_of_calls},
                                                       db_agent_execution.agent_id, organisation_id)
            session.commit()
            logger.info("ITERATION_LIMIT_CROSSED")
            return True
        return False