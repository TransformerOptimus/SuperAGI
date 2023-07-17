import importlib
from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker

import superagi.worker
from superagi.agent.super_agi import SuperAgi
from superagi.config.config import get_config
from superagi.helper.encyption_helper import decrypt_data
from superagi.lib.logger import logger
from superagi.llms.google_palm import GooglePalm
from superagi.llms.llm_model_factory import get_model
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.models.agent_workflow_step import AgentWorkflowStep
from superagi.models.configuration import Configuration
from superagi.models.db import connect_db
from superagi.models.resource import Resource
from superagi.models.tool import Tool
from superagi.models.tool_config import ToolConfig
from superagi.resource_manager.file_manager import FileManager
from superagi.resource_manager.resource_summary import ResourceSummarizer
from superagi.tools.base_tool import BaseToolkitConfiguration
from superagi.tools.resource.query_resource import QueryResourceTool
from superagi.tools.thinking.tools import ThinkingTool
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager
from superagi.types.model_source_types import ModelSourceType
from superagi.types.vector_store_types import VectorStoreType
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory
from superagi.apm.event_handler import EventHandler
# from superagi.helper.tool_helper import get_tool_config_by_key

engine = connect_db()
Session = sessionmaker(bind=engine)


class DBToolkitConfiguration(BaseToolkitConfiguration):
    session: Session
    toolkit_id: int

    def __init__(self, session=None, toolkit_id=None):
        self.session = session
        self.toolkit_id = toolkit_id

    def get_tool_config(self, key: str):
        tool_config = self.session.query(ToolConfig).filter_by(key=key, toolkit_id=self.toolkit_id).first()
        if tool_config and tool_config.value:
            return tool_config.value
        return super().get_tool_config(key=key)


class AgentExecutor:
    @staticmethod
    def validate_filename(filename):
        """
        Validate the filename by removing the last three characters if the filename ends with ".py".

        Args:
            filename (str): The filename.

        Returns:
            str: The validated filename.
        """
        if filename.endswith(".py"):
            return filename[:-3]  # Remove the last three characters (i.e., ".py")
        return filename

    @staticmethod
    def create_object(tool, session):
        """
        Create an object of a agent usable tool dynamically.

        Args:
            tool (Tool) : Tool object from which agent tool would be made.

        Returns:
            object: The object of the agent usable tool.
        """
        file_name = AgentExecutor.validate_filename(filename=tool.file_name)

        tools_dir = get_config("TOOLS_DIR")
        if tools_dir is None:
            tools_dir = "superagi/tools"
        parsed_tools_dir = tools_dir.rstrip("/")
        module_name = ".".join(parsed_tools_dir.split("/") + [tool.folder_name, file_name])

        # module_name = f"superagi.tools.{folder_name}.{file_name}"

        # Load the module dynamically
        module = importlib.import_module(module_name)

        # Get the class from the loaded module
        obj_class = getattr(module, tool.class_name)

        # Create an instance of the class
        new_object = obj_class()
        new_object.toolkit_config = DBToolkitConfiguration(session=session, toolkit_id=tool.toolkit_id)
        return new_object

    @classmethod
    def get_model_api_key_from_execution(cls, model, agent_execution, session):
        """
        Get the model API key from the agent execution.

        Args:
            agent_execution (AgentExecution): The agent execution.
            session (Session): The database session.

        Returns:
            str: The model API key.
        """
        config_model_source = AgentExecutor.get_llm_source(agent_execution, session)
        selected_model_source = ModelSourceType.get_model_source_from_model(model)
        if selected_model_source.value == config_model_source:
            config_value = Configuration.fetch_value_by_agent_id(session, agent_execution.agent_id, "model_api_key")
            model_api_key = decrypt_data(config_value)
            return model_api_key

        if selected_model_source == ModelSourceType.GooglePalm:
            return get_config("PALM_API_KEY")
        return get_config("OPENAI_API_KEY")

    @classmethod
    def get_llm_source(cls, agent_execution, session):
        return Configuration.fetch_value_by_agent_id(session, agent_execution.agent_id, "model_source") or "OpenAi"

    @classmethod
    def get_embedding(cls, model_source, model_api_key):
        if "OpenAi" in model_source:
            return OpenAiEmbedding(api_key=model_api_key)
        if "Google" in model_source:
            return GooglePalm(api_key=model_api_key)
        return None

    @staticmethod
    def get_organisation(agent_execution,session):
        """
        Get the model API key from the agent execution.

        Args:
            agent_execution (AgentExecution): The agent execution.
            session (Session): The database session.

        Returns:
             str: The model API key.
        """
        agent_id = agent_execution.agent_id
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        organisation = agent.get_agent_organisation(session)

        return organisation


    def execute_next_action(self, agent_execution_id):
        """
        Execute the next action of the agent execution.

        Args:
            agent_execution_id (int): The ID of the agent execution.

        Returns:
            None
        """
        global engine
        # try:
        engine.dispose()
        session = Session()
        agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        '''Avoiding running old agent executions'''
        if agent_execution.created_at < datetime.utcnow() - timedelta(days=1):
            return
        agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
        # if agent_execution.status == "PAUSED" or agent_execution.status == "TERMINATED" or agent_execution == "COMPLETED":
        #     return
        if agent_execution.status != "RUNNING" and agent_execution.status != "WAITING_FOR_PERMISSION":
            return

        if not agent:
            return "Agent Not found"

        tools = [
            ThinkingTool()
        ]

        parsed_config = Agent.fetch_configuration(session, agent.id)
        parsed_execution_config = AgentExecutionConfiguration.fetch_configuration(session, agent_execution)
        max_iterations = (parsed_config["max_iterations"])
        total_calls = agent_execution.num_of_calls
        organisation = AgentExecutor.get_organisation(agent_execution, session)

        if max_iterations <= total_calls:
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "ITERATION_LIMIT_EXCEEDED"
            session.commit()
            EventHandler(session=session).create_event('run_iteration_limit_crossed', {'agent_execution_id':db_agent_execution.id,'name': db_agent_execution.name,'tokens_consumed':db_agent_execution.num_of_tokens,"calls":db_agent_execution.num_of_calls}, db_agent_execution.agent_id, organisation.id)
            logger.info("ITERATION_LIMIT_CROSSED")
            return "ITERATION_LIMIT_CROSSED"

        parsed_config["agent_execution_id"] = agent_execution.id

        model_api_key = AgentExecutor.get_model_api_key_from_execution(parsed_config["model"], agent_execution, session)
        model_llm_source = ModelSourceType.get_model_source_from_model(parsed_config["model"]).value
        organisation = AgentExecutor.get_organisation(agent_execution, session)
        try:
            if parsed_config["LTM_DB"] == "Pinecone":
                memory = VectorFactory.get_vector_storage(VectorStoreType.PINECONE, "super-agent-index1",
                                                          AgentExecutor.get_embedding(model_llm_source, model_api_key))
            else:
                memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1",
                                                          AgentExecutor.get_embedding(model_llm_source, model_api_key))
        except:
            logger.info("Unable to setup the pinecone connection...")
            memory = None

        user_tools = session.query(Tool).filter(Tool.id.in_(parsed_config["tools"])).all()
        for tool in user_tools:
            tool = AgentExecutor.create_object(tool, session)
            tools.append(tool)

        resource_summary = self.get_agent_resource_summary(agent_id=agent.id, session=session,
                                                           model_llm_source=model_llm_source,
                                                           default_summary=parsed_config.get("resource_summary"))
        if resource_summary is not None:
            tools.append(QueryResourceTool())

        tools = self.set_default_params_tools(tools, parsed_config, parsed_execution_config, agent_execution.agent_id,
                                              model_api_key=model_api_key,
                                              resource_description=resource_summary,
                                              session=session)

        spawned_agent = SuperAgi(ai_name=parsed_config["name"], ai_role=parsed_config["description"],
                                 llm=get_model(model=parsed_config["model"], api_key=model_api_key), tools=tools,
                                 memory=memory,
                                 agent_config=parsed_config,
                                 agent_execution_config=parsed_execution_config)

        try:
            self.handle_wait_for_permission(agent_execution, spawned_agent, session)
        except ValueError:
            return

        agent_workflow_step = session.query(AgentWorkflowStep).filter(
            AgentWorkflowStep.id == agent_execution.current_step_id).first()

        try:
            response = spawned_agent.execute(agent_workflow_step)
        except RuntimeError as e:
            # If our execution encounters an error we return and attempt to retry
            logger.error("Error executing the agent:", e)
            superagi.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=15)
            session.close()
            return

        if "retry" in response and response["retry"]:
            superagi.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=10)
            session.close()
            return

        agent_execution.current_step_id = agent_workflow_step.next_step_id
        session.commit()
        if response["result"] == "COMPLETE":
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "COMPLETED"
            session.commit()
            EventHandler(session=session).create_event('run_completed', {'agent_execution_id':db_agent_execution.id,'name': db_agent_execution.name,'tokens_consumed':db_agent_execution.num_of_tokens,"calls":db_agent_execution.num_of_calls}, db_agent_execution.agent_id, organisation.id)
        elif response["result"] == "WAITING_FOR_PERMISSION":
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "WAITING_FOR_PERMISSION"
            db_agent_execution.permission_id = response.get("permission_id", None)
            session.commit()
        else:
            logger.info(f"Starting next job for agent execution id: {agent_execution_id}")
            superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())

        session.close()
        engine.dispose()

    def set_default_params_tools(self, tools, parsed_config, parsed_execution_config, agent_id, model_api_key,
                                 session, resource_description=None):
        """
        Set the default parameters for the tools.

        Args:
            tools (list): The list of tools.
            parsed_config (dict): Parsed agent configuration.
            parsed_execution_config (dict): Parsed execution configuration
            agent_id (int): The ID of the agent.
            model_api_key (str): The API key of the model.
            resource_description (str): The description of the resource.

        Returns:
            list: The list of tools with default parameters.
        """
        new_tools = []
        for tool in tools:
            if hasattr(tool, 'goals'):
                tool.goals = parsed_execution_config["goal"]
            if hasattr(tool, 'instructions'):
                tool.instructions = parsed_execution_config["instruction"]
            if hasattr(tool, 'llm') and (parsed_config["model"] == "gpt4" or parsed_config[
                "model"] == "gpt-3.5-turbo") and tool.name != "QueryResource":
                tool.llm = get_model(model="gpt-3.5-turbo", api_key=model_api_key, temperature=0.4)
            elif hasattr(tool, 'llm'):
                tool.llm = get_model(model=parsed_config["model"], api_key=model_api_key, temperature=0.4)
            if hasattr(tool, 'agent_id'):
                tool.agent_id = agent_id
            if hasattr(tool, 'agent_execution_id'):
                tool.agent_execution_id = parsed_config["agent_execution_id"]
            if hasattr(tool, 'resource_manager'):
                tool.resource_manager = FileManager(session=session, agent_id=agent_id,
                                                    agent_execution_id=parsed_config[
                                                        "agent_execution_id"])
            if hasattr(tool, 'tool_response_manager'):
                tool.tool_response_manager = ToolResponseQueryManager(session=session, agent_execution_id=parsed_config[
                    "agent_execution_id"])

            if tool.name == "QueryResource" and resource_description:
                tool.description = tool.description.replace("{summary}", resource_description)
            new_tools.append(tool)
        return tools

    def handle_wait_for_permission(self, agent_execution, spawned_agent, session):
        """
        Handles the wait for permission when the agent execution is waiting for permission.

        Args:
            agent_execution (AgentExecution): The agent execution.
            spawned_agent (SuperAgi): The spawned agent.
            session (Session): The database session object.

        Raises:
            ValueError: If the permission is still pending.
        """
        if agent_execution.status != "WAITING_FOR_PERMISSION":
            return
        agent_execution_permission = session.query(AgentExecutionPermission).filter(
            AgentExecutionPermission.id == agent_execution.permission_id).first()
        if agent_execution_permission.status == "PENDING":
            raise ValueError("Permission is still pending")
        if agent_execution_permission.status == "APPROVED":
            result = spawned_agent.handle_tool_response(agent_execution_permission.assistant_reply).get("result")
        else:
            result = f"User denied the permission to run the tool {agent_execution_permission.tool_name}" \
                     f"{' and has given the following feedback : ' + agent_execution_permission.user_feedback if agent_execution_permission.user_feedback else ''}"

        agent_execution_feed = AgentExecutionFeed(agent_execution_id=agent_execution_permission.agent_execution_id,
                                                  agent_id=agent_execution_permission.agent_id,
                                                  feed=result,
                                                  role="user"
                                                  )
        session.add(agent_execution_feed)
        agent_execution.status = "RUNNING"
        session.commit()

    def get_agent_resource_summary(self, agent_id: int, session: Session, model_llm_source: str, default_summary: str):
        if ModelSourceType.GooglePalm.value in model_llm_source:
            return
        ResourceSummarizer(session=session).generate_agent_summary(agent_id=agent_id,generate_all=True)
        agent_config_resource_summary = session.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "resource_summary").first()
        resource_summary = agent_config_resource_summary.value if agent_config_resource_summary is not None else default_summary
        return resource_summary

    def check_for_resource(self,agent_id: int, session: Session):
        resource = session.query(Resource).filter(Resource.agent_id == agent_id,Resource.channel == 'INPUT').first()
        if resource is None:
            return False
        return True
