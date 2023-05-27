from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent import Agent
from superagi.agent.super_agi import SuperAgi
from superagi.vector_store.vector_factory import VectorFactory
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.models.tool import Tool

from superagi.models.db import connectDB
from sqlalchemy.orm import sessionmaker, query


from superagi.llms.openai import OpenAi
# from superagi.tools.base_tool import FunctionalTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.google_search.google_search import GoogleSearchSchema, GoogleSearchTool
from superagi.tools.google_serp_search.google_serp_search import GoogleSerpTool
# from superagi.tools.twitter.send_tweet import SendTweetTool
# from superagi.vector_store.embedding.openai import OpenAiEmbedding
# from superagi.vector_store.vector_factory import VectorFactory

# from superagi.models.types.agent_with_config import AgentWithConfig
import importlib
import os
import json


engine = connectDB()
Session = sessionmaker(bind=engine)
session = Session()

def validate_filename(filename):
    if filename.endswith(".py"):
        return filename[:-3]  # Remove the last three characters (i.e., ".py")
    return filename


def create_object(class_name,folder_name,file_name):
    file_name = validate_filename(filename=file_name)
    module_name = f"superagi.tools.{folder_name}.{file_name}"
    
    # Load the module dynamically
    module = importlib.import_module(module_name)

    # Get the class from the loaded module
    obj_class = getattr(module, class_name)

    # Create an instance of the class
    new_object = obj_class()
    return new_object


def run_superagi_job(agent_execution):
    agent_execution = AgentExecution.from_json(agent_execution)
    agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
    if not agent:
        return "Agent Not found"

    agent_configurations = session.query(AgentConfiguration).filter_by(agent_id=agent_execution.agent_id).all()
    if not agent_configurations:
        return "Agent configurations not found"

    print("Configuration ",agent_configurations)

    parsed_config = {
        "agent_id":agent.id,
        "agent_execution_id":agent_execution.id,
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
        "memory_window":None
    }

    tools = [
    # GoogleSearchTool(),
    WriteFileTool(),
    GoogleSerpTool()
    ]


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

    if parsed_config["LTM_DB"] == "Pinecone":
        memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
    else:
        memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
    
    user_tools = session.query(Tool).filter(Tool.id.in_(parsed_config["tools"])).all()

    # tools = []

    for tool in user_tools:
        tools.append(create_object(tool.class_name,tool.folder_name,tool.file_name))

    # print("Tools: ",tools)
    # print("Agent Config",parsed_config)

    #TODO: Generate tools array on fly
    spawned_agent = SuperAgi(ai_name=parsed_config["name"],ai_role=parsed_config["description"],llm=OpenAi(model=parsed_config["model"]),tools=tools,memory=memory,agent_config=parsed_config)
    spawned_agent.execute(parsed_config["goal"])

    
    
    
session.commit()
session.close()

