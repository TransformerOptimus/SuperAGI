# from superagi.models.types.agent_with_config import AgentWithConfig
import importlib
import json
from datetime import datetime
from time import time

from celery import Celery
from sqlalchemy.orm import sessionmaker

from superagi import worker
from superagi.agent.super_agi import SuperAgi
from superagi.config.config import get_config
from superagi.llms.openai import OpenAi
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.db import connectDB
from superagi.models.tool import Tool
from superagi.tools.email.read_email import ReadEmailTool
from superagi.tools.email.send_email import SendEmailTool
from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool
from superagi.tools.file.read_file import ReadFileTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.google_search.google_search import GoogleSearchTool
from superagi.tools.thinking.tools import LlmThinkingTool
from superagi.tools.jira.create_issue import CreateIssueTool
from superagi.tools.jira.edit_issue import EditIssueTool
from superagi.tools.jira.get_projects import GetProjectsTool
from superagi.tools.jira.search_issues import SearchJiraTool
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory
import superagi.worker
engine = connectDB()
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
        try:
            engine.dispose()
            session = Session()
            agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
            if agent_execution.status == "PAUSED" or agent_execution.status == "TERMINATED" \
                    or agent_execution == "COMPLETED":
                return

            if not agent:
                return "Agent Not found"
            print("Agent Under Execution : ")
            print(agent)
            print("Agent Execution : ")
            print(agent_execution)
            parsed_config = self.fetch_agent_configuration(session, agent, agent_execution)
            tools = [
                LlmThinkingTool(llm=OpenAi(model=parsed_config["model"])),
                # GoogleSearchTool(),
                # WriteFileTool(),
                # ReadFileTool(),
                # ReadEmailTool(),
                # SendEmailTool(),
                # SendEmailAttachmentTool(),
                # CreateIssueTool(),
                # SearchJiraTool(),
                # GetProjectsTool(),
                # EditIssueTool()
            ]

            if parsed_config["LTM_DB"] == "Pinecone":
                memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
            else:
                memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())

            user_tools = session.query(Tool).filter(Tool.id.in_(parsed_config["tools"])).all()

            for tool in user_tools:
                tools.append(AgentExecutor.create_object(tool.class_name, tool.folder_name, tool.file_name))

            spawned_agent = SuperAgi(ai_name=parsed_config["name"], ai_role=parsed_config["description"],
                                     llm=OpenAi(model=parsed_config["model"]), tools=tools, memory=memory,
                                     agent_config=parsed_config, agent=agent)
            response = spawned_agent.execute(parsed_config["goal"])

            session.commit()
            session.close()
            if response == "COMPLETE":
                db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
                db_agent_execution.status = "COMPLETED"
                session.commit()
                return
            else:
                print("Starting next job for agent execution id: ", agent_execution_id)
                superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())
        except Exception as exception:
            print("Exception Occured in celery job")
            print(str(exception))
        finally:
            engine.dispose()



    def fetch_agent_configuration(self, session, agent, agent_execution):
        agent_configurations = session.query(AgentConfiguration).filter_by(agent_id=agent_execution.agent_id).all()
        print("Configuration ", agent_configurations)
        parsed_config = {
            "agent_id": agent.id,
            "agent_execution_id": agent_execution.id,
            "name": agent.name,
            "project_id": agent.project_id,
            "description": agent.description,
            "goal": [],
            "agent_type": None,
            "constraints": [],
            "tools": [],
            "exit": None,
            "iteration_interval": None,
            "model": None,
            "permission_type": None,
            "LTM_DB": None,
            "memory_window": None
        }
        if not agent_configurations:
            return parsed_config
        for item in agent_configurations:
            key = item.key
            value = item.value

            if key == "name":
                parsed_config["name"] = value
            elif key == "project_id":
                parsed_config["project_id"] = int(value)
            elif key == "description":
                parsed_config["description"] = value
            elif key == "goal":
                parsed_config["goal"] = eval(value)
            elif key == "agent_type":
                parsed_config["agent_type"] = value
            elif key == "constraints":
                parsed_config["constraints"] = eval(value)
            elif key == "tools":
                parsed_config["tools"] = [int(x) for x in json.loads(value)]
            # elif key == "tools":
            # parsed_config["tools"] = eval(value)
            elif key == "exit":
                parsed_config["exit"] = value
            elif key == "iteration_interval":
                parsed_config["iteration_interval"] = int(value)
            elif key == "model":
                parsed_config["model"] = value
            elif key == "permission_type":
                parsed_config["permission_type"] = value
            elif key == "LTM_DB":
                parsed_config["LTM_DB"] = value
            elif key == "memory_window":
                parsed_config["memory_window"] = int(value)
        return parsed_config
