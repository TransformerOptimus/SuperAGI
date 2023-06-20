import importlib
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

import superagi.worker
from superagi.agent.super_agi import SuperAgi
from superagi.config.config import get_config
from superagi.helper.encyption_helper import decrypt_data
from superagi.lib.logger import logger
from superagi.llms.openai import OpenAi
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_workflow_step import AgentWorkflowStep
from superagi.models.configuration import Configuration
from superagi.models.db import connect_db
from superagi.models.organisation import Organisation
from superagi.models.project import Project
from superagi.models.tool import Tool
from superagi.models.tool_config import ToolConfig
from superagi.tools.thinking.tools import ThinkingTool
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory

engine = connect_db()
Session = sessionmaker(bind=engine)


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
    def create_object(tool,session):
        """
        Create an object of a agent usable tool dynamically.

        Args:
            tool (Tool) : Tool object from which agent tool would be made.

        Returns:
            object: The object of the agent usable tool.
        """
        file_name = AgentExecutor.validate_filename(filename=tool.file_name)

        tools_dir = get_config("TOOLS_DIR").rstrip("/")
        module_name = ".".join(tools_dir.split("/") + [tool.folder_name, file_name])

        # module_name = f"superagi.tools.{folder_name}.{file_name}"

        # Load the module dynamically
        module = importlib.import_module(module_name)

        # Get the class from the loaded module
        obj_class = getattr(module, tool.class_name)

        # Create an instance of the class
        new_object = obj_class()
        new_object.tool_kit_id = tool.tool_kit_id
        new_object.session = session
        new_object.set_tool_config_func(ToolConfig.get_tool_config_by_key)
        return new_object

    @staticmethod
    def get_model_api_key_from_execution(agent_execution, session):
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
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        project = session.query(Project).filter(Project.id == agent.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        organisation = session.query(Organisation).filter(Organisation.id == project.organisation_id).first()
        if not organisation:
            raise HTTPException(status_code=404, detail="Organisation not found")
        config = session.query(Configuration).filter(Configuration.organisation_id == organisation.id,
                                                     Configuration.key == "model_api_key").first()
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        model_api_key = decrypt_data(config.value)
        return model_api_key

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
        if agent_execution.status != "RUNNING":
            return

        if not agent:
            return "Agent Not found"

        tools = [
            ThinkingTool()
        ]

        parsed_config = Agent.fetch_configuration(session, agent.id)
        max_iterations = (parsed_config["max_iterations"])
        total_calls = agent_execution.num_of_calls

        if max_iterations <= total_calls:
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "ITERATION_LIMIT_EXCEEDED"
            session.commit()
            logger.info("ITERATION_LIMIT_CROSSED")
            return "ITERATION_LIMIT_CROSSED"

        parsed_config["agent_execution_id"] = agent_execution.id

        model_api_key = AgentExecutor.get_model_api_key_from_execution(agent_execution, session)

        try:
            if parsed_config["LTM_DB"] == "Pinecone":
                memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1",
                                                          OpenAiEmbedding(model_api_key))
            else:
                memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1",
                                                          OpenAiEmbedding(model_api_key))
        except:
            logger.info("Unable to setup the pinecone connection...")
            memory = None

        user_tools = session.query(Tool).filter(Tool.id.in_(parsed_config["tools"])).all()
        for tool in user_tools:
            tool = AgentExecutor.create_object(tool,session)
            tools.append(tool)

        tools = self.set_default_params_tools(tools, parsed_config, agent_execution.agent_id,
                                              model_api_key=model_api_key)
        # print("final tools ________________")
        # print(tools)
        # for tool in tools:
        #     print(tool)
        #     print("It belongs to ",tool.tool_kit_id)
        spawned_agent = SuperAgi(ai_name=parsed_config["name"], ai_role=parsed_config["description"],
                                 llm=OpenAi(model=parsed_config["model"], api_key=model_api_key), tools=tools,
                                 memory=memory,
                                 agent_config=parsed_config)

        agent_workflow_step = session.query(AgentWorkflowStep).filter(
            AgentWorkflowStep.id == agent_execution.current_step_id).first()
        response = spawned_agent.execute(agent_workflow_step)
        if "retry" in response and response["retry"]:
            response = spawned_agent.execute(agent_workflow_step)
        agent_execution.current_step_id = agent_workflow_step.next_step_id
        session.commit()
        if response["result"] == "COMPLETE":
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "COMPLETED"

            session.commit()
        else:
            logger.info("Starting next job for agent execution id: ", agent_execution_id)
            superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())

        session.close()
        # except Exception as exception:
        #      print("Exception Occured in celery job", exception)
        #      print(str(exception))
        # finally:
        engine.dispose()

    def set_default_params_tools(self, tools, parsed_config, agent_id, model_api_key):
        """
        Set the default parameters for the tools.

        Args:
            tools (list): The list of tools.
            parsed_config (dict): The parsed configuration.
            agent_id (int): The ID of the agent.
            model_api_key (str): The API key of the model.

        Returns:
            list: The list of tools with default parameters.
        """
        new_tools = []
        for tool in tools:
            if hasattr(tool, 'goals'):
                tool.goals = parsed_config["goal"]
            if hasattr(tool, 'llm') and (parsed_config["model"] == "gpt4" or parsed_config["model"] == "gpt-3.5-turbo"):
                tool.llm = OpenAi(model="gpt-3.5-turbo", api_key=model_api_key, temperature=0.3)
            elif hasattr(tool, 'llm'):
                tool.llm = OpenAi(model=parsed_config["model"], api_key=model_api_key, temperature=0.3)
            if hasattr(tool, 'image_llm'):
                tool.image_llm = OpenAi(model=parsed_config["model"], api_key=model_api_key)
            if hasattr(tool, 'agent_id'):
                tool.agent_id = agent_id
            new_tools.append(tool)
        return tools
