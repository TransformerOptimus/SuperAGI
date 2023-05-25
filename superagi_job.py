from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent import Agent
# from fastapi_sqlalchemy import DBSessionMiddleware, db
from superagi.agent.super_agi import SuperAgi
from superagi.vector_store.vector_factory import VectorFactory
from superagi.vector_store.embedding.openai import OpenAiEmbedding

from superagi.models.db import connectDB
# from fastapi_sqlalchemy import db
from sqlalchemy.orm import sessionmaker, query



# from superagi.agent.super_agi import SuperAgi
from superagi.llms.openai import OpenAi
# from superagi.tools.base_tool import FunctionalTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.google_search.tools import GoogleSearchSchema, GoogleSearchTool
from superagi.tools.google_serp_search.tools import GoogleSerpTool
# from superagi.tools.twitter.send_tweet import SendTweetTool
# from superagi.vector_store.embedding.openai import OpenAiEmbedding
# from superagi.vector_store.vector_factory import VectorFactory


engine = connectDB()
Session = sessionmaker(bind=engine)
session = Session()


def run_superagi_job(agent_execution : AgentExecution):
    print("New Agent Exec : ",agent_execution)
    agent_execution = AgentExecution.from_json(agent_execution)
    print("New Agent Exec : ",agent_execution)
    agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
    if not agent:
        return "Agent Not found"

    agent_configurations = session.query(AgentConfiguration).filter_by(agent_id=agent_execution.agent_id).all()
    if not agent_configurations:
        return "Agent configurations not found"

    parsed_config = {
        "agent_id":agent.id,
        "name": agent.name,
        "project_id": agent.project_id,
        "description": agent.description,
        "goal": [],
        "agent_type": None,
        "constraints": None,
        "tools": [],
        "exit": None,
        "iteration_interval": None,
        "model": None,
        "permission_type": None,
        "LTM_DB": None,
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
            parsed_config["goal"] = eval(value)  # Using eval to parse the list of strings
        elif key == "agent_type":
            parsed_config["agent_type"] = value
        elif key == "constraints":
            parsed_config["constraints"] = value
        elif key == "tools":
            parsed_config["tools"] = eval(value)  # Using eval to parse the list of strings
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

    if parsed_config["LTM_DB"] == "Pinecone":
        memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
    else:
        memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
    spawned_agent = SuperAgi(ai_name=parsed_config["name"],ai_role=parsed_config["description"],llm=OpenAi(model=parsed_config["model"]),tools=tools,memory=memory)
    spawned_agent.execute(parsed_config["goal"])
    
    
session.commit()

