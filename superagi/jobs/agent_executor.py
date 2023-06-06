# from superagi.models.types.agent_with_config import AgentWithConfig
import importlib
from datetime import datetime, timedelta
from time import time

from celery import Celery
from sqlalchemy.orm import sessionmaker
from ast import literal_eval

from superagi import worker
from superagi.agent.super_agi import SuperAgi
from superagi.config.config import get_config
from superagi.llms.openai import OpenAi
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_template_step import AgentTemplateStep
from superagi.models.db import connect_db
from superagi.models.tool import Tool
from superagi.tools.code.tools import CodingTool
from superagi.tools.email.read_email import ReadEmailTool
from superagi.tools.email.send_email import SendEmailTool
from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool
from superagi.tools.file.read_file import ReadFileTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.google_search.google_search import GoogleSearchTool
from superagi.tools.google_serp_search.google_serp_search import GoogleSerpTool
from superagi.tools.jira.create_issue import CreateIssueTool
from superagi.tools.jira.edit_issue import EditIssueTool
from superagi.tools.jira.get_projects import GetProjectsTool
from superagi.tools.jira.search_issues import SearchJiraTool
from superagi.tools.thinking.tools import ReasoningTool
from superagi.tools.webscaper.tools import WebScraperTool
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory
import superagi.worker
engine = connect_db()
Session = sessionmaker(bind=engine)

class AgentExecutor:
    @staticmethod
    def validate_filename(filename):
        if filename.endswith(".py"):
            return filename[:-3]  # Remove the last three characters (i.e., ".py")
        return filename

    @staticmethod
    def create_object(class_name, folder_name, file_name):
        file_name = AgentExecutor.validate_filename(filename=file_name)
        module_name = f"superagi.tools.{folder_name}.{file_name}"

        # Load the module dynamically
        module = importlib.import_module(module_name)

        # Get the class from the loaded module
        obj_class = getattr(module, class_name)

        # Create an instance of the class
        new_object = obj_class()
        return new_object

    def execute_next_action(self, agent_execution_id):
        global engine
        # try:
        engine.dispose()
        session = Session()
        agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        '''Avoiding running old agent executions'''
        if agent_execution.created_at < datetime.utcnow() - timedelta(days=1):
            return
        agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
        if agent_execution.status == "PAUSED" or agent_execution.status == "TERMINATED" or agent_execution == "COMPLETED":
            return

        if not agent:
            return "Agent Not found"

        tools = [
            GoogleSerpTool(),
            WriteFileTool(),
            ReadFileTool(),
            ReasoningTool(),
            CodingTool(),
            WebScraperTool(),
        ]

        parsed_config = Agent.fetch_configuration(session, agent.id)
        #print(parsed_config)
        parsed_config["agent_execution_id"] = agent_execution.id
        if parsed_config["LTM_DB"] == "Pinecone":
            memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
        else:
            memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())

        user_tools = session.query(Tool).filter(Tool.id.in_(parsed_config["tools"])).all()
        for tool in user_tools:
            tool = AgentExecutor.create_object(tool.class_name, tool.folder_name, tool.file_name)
            tools.append(tool)

        tools = self.set_default_params_tools(tools, parsed_config, agent_execution.agent_id)

        # TODO: Generate tools array on fly
        spawned_agent = SuperAgi(ai_name=parsed_config["name"], ai_role=parsed_config["description"],
                                 llm=OpenAi(model=parsed_config["model"]), tools=tools, memory=memory,
                                 agent_config=parsed_config)


        agent_template_step = session.query(AgentTemplateStep).filter(AgentTemplateStep.id == agent_execution.current_step_id).first()
        response = spawned_agent.execute(agent_template_step)
        if "retry" in response and response["retry"]:
            response = spawned_agent.execute(agent_template_step)
        agent_execution.current_step_id = agent_template_step.next_step_id
        session.commit()
        if response["result"] == "COMPLETE":
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "COMPLETED"
            session.commit()
        else:
            print("Starting next job for agent execution id: ", agent_execution_id)
            superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())

        session.close()
        # except Exception as exception:
        #     print("Exception Occured in celery job", exception)
        #     print(str(exception))
        # finally:
        #     engine.dispose()

    def set_default_params_tools(self, tools, parsed_config, agent_id):
        new_tools = []
        for tool in tools:
            if hasattr(tool, 'goals'):
                tool.goals = parsed_config["goal"]
            if hasattr(tool, 'llm') and (parsed_config["model"] == "gpt4" or parsed_config["model"] == "gpt-3.5-turbo"):
                tool.llm = OpenAi(model="gpt-3.5-turbo")
            elif hasattr(tool, 'llm'):
                tool.llm = OpenAi(model=parsed_config["model"])
            elif hasattr(tool, 'agent_id'):
                tool.agent_id = agent_id
            new_tools.append(tool)
        return tools