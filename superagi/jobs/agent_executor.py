from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker
from superagi.llms.local_llm import LocalLLM

import superagi.worker
from superagi.agent.agent_iteration_step_handler import AgentIterationStepHandler
from superagi.agent.agent_tool_step_handler import AgentToolStepHandler
from superagi.agent.agent_workflow_step_wait_handler import AgentWaitStepHandler
from superagi.agent.types.wait_step_status import AgentWorkflowStepWaitStatus
from superagi.apm.event_handler import EventHandler
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.google_palm import GooglePalm
from superagi.llms.hugging_face import HuggingFace
from superagi.llms.llm_model_factory import get_model
from superagi.llms.replicate import Replicate
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.db import connect_db
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_wait import AgentWorkflowStepWait
from superagi.types.vector_store_types import VectorStoreType
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory
from superagi.worker import execute_agent
from superagi.agent.types.agent_workflow_step_action_types import AgentWorkflowStepAction
from superagi.agent.types.agent_execution_status import AgentExecutionStatus

# from superagi.helper.tool_helper import get_tool_config_by_key

engine = connect_db()
Session = sessionmaker(bind=engine)


class AgentExecutor:

    def execute_next_step(self, agent_execution_id):
        global engine
        # try:
        engine.dispose()
        session = Session()
        try:
            agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            '''Avoiding running old agent executions'''
            if agent_execution and agent_execution.created_at < datetime.utcnow() - timedelta(days=1):
                logger.error("Older agent execution found, skipping execution")
                return

            agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
            agent_config = Agent.fetch_configuration(session, agent.id)
            if agent.is_deleted or (
                    agent_execution.status != AgentExecutionStatus.RUNNING.value and agent_execution.status != AgentExecutionStatus.WAITING_FOR_PERMISSION.value):
                logger.error(f"Agent execution stopped. {agent.id}: {agent_execution.status}")
                return

            organisation = Agent.find_org_by_agent_id(session, agent_id=agent.id)
            if self._check_for_max_iterations(session, organisation.id, agent_config, agent_execution_id):
                logger.error(f"Agent execution stopped. Max iteration exceeded. {agent.id}: {agent_execution.status}")
                return

            try:
                model_config = AgentConfiguration.get_model_api_key(session, agent_execution.agent_id,
                                                                    agent_config["model"])
                model_api_key = model_config['api_key']
                model_llm_source = model_config['provider']
            except Exception as e:
                logger.info(f"Unable to get model config...{e}")
                return

            try:
                memory = None
                if "OpenAI" in model_llm_source:
                    vector_store_type = VectorStoreType.get_vector_store_type(get_config("LTM_DB", "Redis"))
                    memory = VectorFactory.get_vector_storage(vector_store_type, "super-agent-index1",
                                                              AgentExecutor.get_embedding(model_llm_source,
                                                                                          model_api_key))
            except Exception as e:
                logger.info(f"Unable to setup the connection...{e}")
                memory = None

            agent_workflow_step = session.query(AgentWorkflowStep).filter(
                AgentWorkflowStep.id == agent_execution.current_agent_step_id).first()
            try:
                self.__execute_workflow_step(agent, agent_config, agent_execution_id, agent_workflow_step, memory,
                                             model_api_key, organisation, session)

            except Exception as e:
                logger.info("Exception in executing the step: {}".format(e))
                superagi.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=15)
                return

            agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            if agent_execution.status == "COMPLETED" or agent_execution.status == "WAITING_FOR_PERMISSION":
                logger.info("Agent Execution is completed or waiting for permission")
                session.close()
                return
            superagi.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=2)
            # superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())
        finally:
            session.close()
            engine.dispose()

    def __execute_workflow_step(self, agent, agent_config, agent_execution_id, agent_workflow_step, memory,
                                model_api_key, organisation, session):
        logger.info("Executing Workflow step : ", agent_workflow_step.action_type)
        if agent_workflow_step.action_type == AgentWorkflowStepAction.TOOL.value:
            tool_step_handler = AgentToolStepHandler(session,
                                                     llm=get_model(model=agent_config["model"], api_key=model_api_key,
                                                                   organisation_id=organisation.id)
                                                     , agent_id=agent.id, agent_execution_id=agent_execution_id,
                                                     memory=memory)
            tool_step_handler.execute_step()
        elif agent_workflow_step.action_type == AgentWorkflowStepAction.ITERATION_WORKFLOW.value:
            iteration_step_handler = AgentIterationStepHandler(session,
                                                               llm=get_model(model=agent_config["model"],
                                                                             api_key=model_api_key,
                                                                             organisation_id=organisation.id)
                                                               , agent_id=agent.id,
                                                               agent_execution_id=agent_execution_id, memory=memory)
            print(get_model(model=agent_config["model"], api_key=model_api_key, organisation_id=organisation.id))
            iteration_step_handler.execute_step()
        elif agent_workflow_step.action_type == AgentWorkflowStepAction.WAIT_STEP.value:
            (AgentWaitStepHandler(session=session, agent_id=agent.id,
                                  agent_execution_id=agent_execution_id)
             .execute_step())

    @classmethod
    def get_embedding(cls, model_source, model_api_key):
        if "OpenAI" in model_source:
            return OpenAiEmbedding(api_key=model_api_key)
        if "Google" in model_source:
            return GooglePalm(api_key=model_api_key)
        if "Hugging" in model_source:
            return HuggingFace(api_key=model_api_key)
        if "Replicate" in model_source:
            return Replicate(api_key=model_api_key)
        if "Custom" in model_source:
            return LocalLLM()
        return None

    def _check_for_max_iterations(self, session, organisation_id, agent_config, agent_execution_id):
        db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        if agent_config["max_iterations"] <= db_agent_execution.num_of_calls:
            db_agent_execution.status = AgentExecutionStatus.ITERATION_LIMIT_EXCEEDED.value

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

    def execute_waiting_workflows(self):
        """Check if wait time of wait workflow step is over and can be resumed."""

        session = Session()
        waiting_agent_executions = session.query(AgentExecution).filter(
            AgentExecution.status == AgentExecutionStatus.WAIT_STEP.value,
        ).all()
        for agent_execution in waiting_agent_executions:
            workflow_step = session.query(AgentWorkflowStep).filter(
                AgentWorkflowStep.id == agent_execution.current_agent_step_id).first()
            step_wait = AgentWorkflowStepWait.find_by_id(session, workflow_step.action_reference_id)
            if step_wait is not None:
                wait_time = step_wait.delay if not None else 0
                logger.info(f"Agent Execution ID: {agent_execution.id}")
                logger.info(f"Wait time: {wait_time}")
                logger.info(f"Wait begin time: {step_wait.wait_begin_time}")
                logger.info(f"Current time: {datetime.now()}")
                logger.info(f"Wait Difference : {(datetime.now() - step_wait.wait_begin_time).total_seconds()}")
                if ((datetime.now() - step_wait.wait_begin_time).total_seconds() > wait_time
                        and step_wait.status == AgentWorkflowStepWaitStatus.WAITING.value):
                    agent_execution.status = AgentExecutionStatus.RUNNING.value
                    step_wait.status = AgentWorkflowStepWaitStatus.COMPLETED.value
                    session.commit()
                    session.flush()
                    AgentWaitStepHandler(session=session, agent_id=agent_execution.agent_id,
                                         agent_execution_id=agent_execution.id).handle_next_step()
                    execute_agent.delay(agent_execution.id, datetime.now())
        session.close()