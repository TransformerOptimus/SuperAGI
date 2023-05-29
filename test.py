from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.file.read_file import ReadFileTool
from superagi.tools.twitter.send_tweet import SendTweetTool
from superagi.tools.thinking.tools import LlmThinkingTool
from superagi.tools.email.read_email import ReadEmailTool
from superagi.tools.email.send_email import SendEmailTool
from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory
from superagi.tools.google_search.google_search import GoogleSearchSchema, GoogleSearchTool
from superagi.tools.google_serp_search.google_serp_search import GoogleSerpTool
from superagi.models.agent_config import AgentConfiguration
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

import argparse

parser = argparse.ArgumentParser(description='Create a new agent.')
parser.add_argument('--name', type=str, help='Agent name for the script.')
parser.add_argument('--description', type=str, help='Agent description for the script.')
parser.add_argument('--goals', type=str, nargs='+', help='Agent goals for the script.')
args = parser.parse_args()

agent_name = args.name
agent_description = args.description
agent_goals = args.goals

engine = connectDB()
Session = sessionmaker(bind=engine)
session = Session()

def ask_user_for_goals():
    goals = []
    while True:
        goal = input("Enter a goal (or 'q' to quit): ")
        if goal == 'q':
            break
        goals.append(goal)
    return goals



def run_superagi_cli(agent_name=None,agent_description=None,agent_goals=None):
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
    if agent_name is None:
        agent_name = input("Enter agent name: ")
    if agent_description is None:
        agent_description = input("Enter agent description: ")
    agent = Agent(name=agent_name, description=agent_description, project_id=project.id)
    session.add(agent)
    session.flush()
    session.commit()
    print(agent)

    #Agent Config
    # Create Agent Configuration
    agent_config_values = {
        "goal": ask_user_for_goals() if agent_goals is None else agent_goals,
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
    
run_superagi_cli(agent_name=agent_name,agent_description=agent_description,agent_goals=agent_goals)
