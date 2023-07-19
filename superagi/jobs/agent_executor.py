from datetime import datetime, timedelta

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
        global engine
        # try:
        engine.dispose()
        session = Session()
        agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        '''Avoiding running old agent executions'''
        if agent_execution.created_at < datetime.utcnow() - timedelta(days=1):
            return

        agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
        agent_config = Agent.fetch_configuration(session, agent.id)
        if agent.is_deleted or (
                agent_execution.status != "RUNNING" and agent_execution.status != "WAITING_FOR_PERMISSION"):
            return

        if self._check_for_max_iterations(session, agent.organisation_id, agent_config, agent_execution_id):
            return

        model_api_key = AgentConfiguration.get_model_api_key(session, agent_execution.agent_id, agent_config["model"])
        model_llm_source = ModelSourceType.get_model_source_from_model(agent_config["model"]).value
        try:
            vector_store_type = VectorStoreType.get_vector_store_type(agent_config["LTM_DB"])
            memory = VectorFactory.get_vector_storage(vector_store_type, "super-agent-index1",
                                                      AgentExecutor._get_embedding(model_llm_source, model_api_key))
        except:
            logger.info("Unable to setup the pinecone connection...")
            memory = None

        agent_workflow_step = session.query(AgentWorkflowStep).filter(
            AgentWorkflowStep.id == agent_execution.current_step_id).first()
        if agent_workflow_step.action_type == "TOOL":
            tool_step_handler = AgentToolStepHandler(session,
                                                     llm=get_model(model=agent_config["model"], api_key=model_api_key)
                                                     , agent_id=agent.id, agent_execution_id=agent_execution_id,
                                                     memory=memory)
            tool_step_handler.execute_step(agent_execution.current_step_id)
        elif agent_workflow_step.action_type == "ITERATION_WORKFLOW":
            iteration_step_handler = AgentIterationStepHandler(session,
                                                          llm=get_model(model=agent_config["model"],
                                                                        api_key=model_api_key)
                                                               , agent_id=agent.id,
                                                               agent_execution_id=agent_execution_id, memory=memory)
            iteration_step_handler.execute_step(agent_execution.current_step_id)

        agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        if agent_execution.status == "COMPLETED" or agent_execution.status == "WAITING_FOR_PERMISSION":
            return
        superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())

        session.close()
        engine.dispose()

    @classmethod
    def _get_embedding(cls, model_source, model_api_key):
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
    #
    # def execute_next_action(self, agent_execution_id):
    #     """
    #     Execute the next action of the agent execution.
    #
    #     Args:
    #         agent_execution_id (int): The ID of the agent execution.
    #
    #     Returns:
    #         None
    #     """
    #     global engine
    #     # try:
    #     engine.dispose()
    #     session = Session()
    #     agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    #     '''Avoiding running old agent executions'''
    #     if agent_execution.created_at < datetime.utcnow() - timedelta(days=1):
    #         return
    #     agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
    #     if agent_execution.status != "RUNNING" and agent_execution.status != "WAITING_FOR_PERMISSION":
    #         return
    #
    #     if not agent:
    #         return "Agent Not found"
    #
    #
    #     agent_config = Agent.fetch_configuration(session, agent.id)
    #     agent_execution_config = AgentExecutionConfiguration.fetch_configuration(session, agent_execution.id)
    #     organisation = Organisation.find_org_by_agent_id(session, agent_id=agent.id)
    #
    #     if agent_config["max_iterations"] <= agent_execution.num_of_calls:
    #         db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    #         db_agent_execution.status = "ITERATION_LIMIT_EXCEEDED"
    #         session.commit()
    #         EventHandler(session=session).create_event('run_iteration_limit_crossed', {'agent_execution_id':db_agent_execution.id,'name': db_agent_execution.name,'tokens_consumed':db_agent_execution.num_of_tokens,"calls":db_agent_execution.num_of_calls}, db_agent_execution.agent_id, organisation.id)
    #         logger.info("ITERATION_LIMIT_CROSSED")
    #         return "ITERATION_LIMIT_CROSSED"
    #
    #     agent_config["agent_execution_id"] = agent_execution.id
    #     model_api_key = AgentConfiguration.get_model_api_key(session, agent_execution.agent_id, agent_config["model"])
    #     model_llm_source = ModelSourceType.get_model_source_from_model(agent_config["model"]).value
    #     try:
    #         vector_store_type = VectorStoreType.get_vector_store_type(agent_config["LTM_DB"])
    #         memory = VectorFactory.get_vector_storage(vector_store_type, "super-agent-index1",
    #                                                   AgentExecutor.get_embedding(model_llm_source, model_api_key))
    #     except:
    #         logger.info("Unable to setup the pinecone connection...")
    #         memory = None
    #
    #     user_tools = session.query(Tool).filter(and_(Tool.id.in_(agent_config["tools"]), Tool.file_name is not None)).all()
    #     tool_builder = ToolBuilder(session, agent.id, agent_execution.id)
    #
    #     resource_summary = ResourceSummarizer(session=session, agent_id=agent.id).fetch_or_create_agent_resource_summary(
    #         default_summary=agent_config.get("resource_summary"))
    #     agent_tools = [
    #         ThinkingTool()
    #     ]
    #     if resource_summary is not None:
    #         agent_tools.append(QueryResourceTool())
    #
    #     for tool in user_tools:
    #         agent_tools.append(tool_builder.build_tool(tool))
    #
    #     agent_tools = [tool_builder.set_default_params_tool(tool, agent_config, agent_execution_config,
    #                                                         model_api_key, resource_summary) for tool in agent_tools]
    #
    #
    #     spawned_agent = SuperAgi(ai_name=agent_config["name"], ai_role=agent_config["description"],
    #                              llm=get_model(model=agent_config["model"], api_key=model_api_key), tools=agent_tools,
    #                              memory=memory,
    #                              agent_config=agent_config,
    #                              agent_execution_config=agent_execution_config)
    #
    #     try:
    #         self.handle_wait_for_permission(agent_execution, spawned_agent, session)
    #     except ValueError:
    #         return
    #
    #     agent_workflow_step = session.query(AgentWorkflowStep).filter(
    #         AgentWorkflowStep.id == agent_execution.current_step_id).first()
    #
    #     try:
    #         response = spawned_agent.execute(agent_workflow_step)
    #     except RuntimeError as e:
    #         # If our execution encounters an error we return and attempt to retry
    #         logger.error("Error executing the agent:", e)
    #         superagi.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=15)
    #         session.close()
    #         return
    #
    #     if "retry" in response and response["retry"]:
    #         superagi.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=15)
    #         session.close()
    #         return
    #
    #     agent_execution.current_step_id = agent_workflow_step.next_step_id
    #     session.commit()
    #     if response["result"] == "COMPLETE":
    #         db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    #         db_agent_execution.status = "COMPLETED"
    #         session.commit()
    #         EventHandler(session=session).create_event('run_completed', {'agent_execution_id':db_agent_execution.id,'name': db_agent_execution.name,'tokens_consumed':db_agent_execution.num_of_tokens,"calls":db_agent_execution.num_of_calls}, db_agent_execution.agent_id, organisation.id)
    #     elif response["result"] == "WAITING_FOR_PERMISSION":
    #         db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    #         db_agent_execution.status = "WAITING_FOR_PERMISSION"
    #         db_agent_execution.permission_id = response.get("permission_id", None)
    #         session.commit()
    #     else:
    #         logger.info(f"Starting next job for agent execution id: {agent_execution_id}")
    #         superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())
    #
    #     session.close()
    #     engine.dispose()
    #
    # def handle_wait_for_permission(self, agent_execution, spawned_agent, session):
    #     """
    #     Handles the wait for permission when the agent execution is waiting for permission.
    #
    #     Args:
    #         agent_execution (AgentExecution): The agent execution.
    #         spawned_agent (SuperAgi): The spawned agent.
    #         session (Session): The database session object.
    #
    #     Raises:
    #         ValueError: If the permission is still pending.
    #     """
    #     if agent_execution.status != "WAITING_FOR_PERMISSION":
    #         return
    #     agent_execution_permission = session.query(AgentExecutionPermission).filter(
    #         AgentExecutionPermission.id == agent_execution.permission_id).first()
    #     if agent_execution_permission.status == "PENDING":
    #         raise ValueError("Permission is still pending")
    #     if agent_execution_permission.status == "APPROVED":
    #         ToolOutputHandler(agent_execution.id)
    #         result = spawned_agent.handle_tool_response(session, agent_execution_permission.assistant_reply).get("result")
    #     else:
    #         result = f"User denied the permission to run the tool {agent_execution_permission.tool_name}" \
    #                  f"{' and has given the following feedback : ' + agent_execution_permission.user_feedback if agent_execution_permission.user_feedback else ''}"
    #
    #     agent_execution_feed = AgentExecutionFeed(agent_execution_id=agent_execution_permission.agent_execution_id,
    #                                               agent_id=agent_execution_permission.agent_id,
    #                                               feed=result,
    #                                               role="user"
    #                                               )
    #     session.add(agent_execution_feed)
    #     agent_execution.status = "RUNNING"
    #     session.commit()

