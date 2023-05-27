# from superagi.agent.super_agi import SuperAgi
# from superagi.llms.openai import OpenAi
# from superagi.tools.base_tool import FunctionalTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.file.read_file import ReadFileTool
from superagi.tools.google_search.tools import GoogleSearchSchema, GoogleSearchTool
from superagi.tools.google_serp_search.tools import GoogleSerpTool
from superagi.models.agent_config import AgentConfiguration
# from superagi.tools.twitter.send_tweet import SendTweetTool
# from superagi.vector_store.embedding.openai import OpenAiEmbedding
# from superagi.vector_store.vector_factory import VectorFactory
# import importlib
# from superagi.tools.twitter.send_tweet import SendTweetTool
# from superagi.tools.email.read_email import ReadEmailTool
# from superagi.tools.email.send_email import SendEmailTool
# from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool
# from superagi.vector_store.embedding.openai import OpenAiEmbedding
# from superagi.vector_store.vector_factory import VectorFactory

# memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
# # memory.add_documents([Document("Hello world")])
# # memory.get_matching_text("Hello world")

# def test_function(name: str):
#     print("hello ramram", name)
#     return

# def create_campaign(campaign_name: str):
#     print("create campaigns", campaign_name)
#     return

# def validate_filename(filename):
#     if filename.endswith(".py"):
#         return filename[:-3]  # Remove the last three characters (i.e., ".py")
#     return filename


# def create_object(class_name,folder_name,file_name):
#     file_name = validate_filename(filename=file_name)
#     module_name = f"superagi.tools.{folder_name}.{file_name}"
    
#     # Load the module dynamically
#     module = importlib.import_module(module_name)

#     # Get the class from the loaded module
#     obj_class = getattr(module, class_name)

#     # Create an instance of the class
#     new_object = obj_class()
#     return new_object

# tools = [
#     GoogleSearchTool(),
#     WriteFileTool(),
#     # GoogleSerpTool()
# ]

# # result = GoogleSearchTool().execute({"query": "List down top 10 marketing strategies for a new product"})
# # print(result)
# # print(result.split("."))
# # send_tool = SendTweetTool()
# # send_tool.execute("Innovation isn't a one-time event; it's a culture. It's about daring to question the status quo, nurturing a curiosity that stretches horizons, and constantly seeking new ways to add value #Innovation #ChangeTheWorld")



# superagi = SuperAgi.from_llm_and_tools("Super AGI", "To solve any complex problems for you", memory, tools, OpenAi(model="gpt-4"))
# user_goal=[]
# user_goal=str(input("Enter your Goals seperated by ',':\n")).split(",")
# superagi.execute(user_goal)

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.organisation import Organisation
from superagi.models.project import Project
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from datetime import datetime


from superagi.models.db import connectDB
from sqlalchemy.orm import sessionmaker, query

from celery_app import test_fucntion

engine = connectDB()
Session = sessionmaker(bind=engine)
session = Session()

# session.query(Agent).delete()
# session.commit()
# session.close()



def ask_user_for_goals():
    goals = []
    while True:
        goal = input("Enter a goal (or 'q' to quit): ")
        if goal == 'q':
            break
        goals.append(goal)
    return goals



def run_superagi_cli():
    # Create default organization
    organization = Organisation(name='Default Organization', description='Default organization description')
    session.add(organization)
    session.flush()  # Flush pending changes to generate the agent's ID
    session.commit()
    print(organization)
   
    # Create default project associated with the organization
    project = Project(name='Default Project', description='Default project description', organisation_id=organization.id)   
    session.add(project)
    session.flush()  # Flush pending changes to generate the agent's ID
    session.commit()
    print(project)

    #Agent 
    agent_name = input("Enter agent name: ")
    agent_description = input("Enter agent description: ")
    agent = Agent(name=agent_name, description=agent_description, project_id=project.id)
    session.add(agent)
    session.flush()
    session.commit()
    print(agent)

    #Agent Config
    # Create Agent Configuration
    agent_config_values = {
        "goal": ask_user_for_goals(),
        "agent_type": "Type Non-Queue",
        "constraints": [  "~4000 word limit for short term memory. ",
                "Your short term memory is short, so immediately save important information to files.",
                "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
                "No user assistance",
                "Exclusively use the commands listed in double quotes e.g. \"command name\""
                ],
        "tools": [],
        "exit": "Default",
        "iteration_interval": 0,
        "model": "gpt-4",
        "permission_type": "Default",
        "LTM_DB": "Pinecone",
        "memory_window":10
    }

    # print("Id is ")
    # print(db_agent.id)
    agent_configurations = [
        AgentConfiguration(agent_id=agent.id, key=key, value=str(value))
        for key, value in agent_config_values.items()
    ]

    session.add_all(agent_configurations)
    session.commit()
    print("Agent Config : ")
    print(agent_configurations)

    # Create agent execution in RUNNING state associated with the agent
    execution = AgentExecution(status='RUNNING', agent_id=agent.id, last_execution_time=datetime.utcnow())
    session.add(execution)
    session.commit()

    print("Final Execution")
    print(execution)

    test_fucntion.delay(execution.to_json())

    print("_________________________________View in Celery CLI________________________________")
    
run_superagi_cli()