import argparse
from datetime import datetime
from time import time
from superagi.lib.logger import logger

from sqlalchemy.orm import sessionmaker

from superagi.worker import execute_agent
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.db import connect_db
from superagi.models.organisation import Organisation
from superagi.models.project import Project

parser = argparse.ArgumentParser(description='Create a new agent.')
parser.add_argument('--name', type=str, help='Agent name for the script.')
parser.add_argument('--description', type=str, help='Agent description for the script.')
parser.add_argument('--goals', type=str, nargs='+', help='Agent goals for the script.')
args = parser.parse_args()

agent_name = args.name
agent_description = args.description
agent_goals = args.goals

engine = connect_db()
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


def run_superagi_cli(agent_name=None, agent_description=None, agent_goals=None):
    # Create default organization
    organization = Organisation(name='Default Organization', description='Default organization description')
    session.add(organization)
    session.flush()  # Flush pending changes to generate the agent's ID
    session.commit()
    logger.info(organization)

    # Create default project associated with the organization
    project = Project(name='Default Project', description='Default project description',
                      organisation_id=organization.id)
    session.add(project)
    session.flush()  # Flush pending changes to generate the agent's ID
    session.commit()
    logger.info(project)

    # Agent
    if agent_name is None:
        agent_name = input("Enter agent name: ")
    if agent_description is None:
        agent_description = input("Enter agent description: ")
    agent = Agent(name=agent_name, description=agent_description, project_id=project.id)
    session.add(agent)
    session.flush()
    session.commit()
    logger.info(agent)

    # Agent Config
    # Create Agent Configuration
    agent_config_values = {
        "goal": ask_user_for_goals() if agent_goals is None else agent_goals,
        "agent_type": "Type Non-Queue",
        "constraints": ["~4000 word limit for short term memory. ",
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
        "memory_window": 10
    }

    agent_configurations = [
        AgentConfiguration(agent_id=agent.id, key=key, value=str(value))
        for key, value in agent_config_values.items()
    ]

    session.add_all(agent_configurations)
    session.commit()
    logger.info("Agent Config : ")
    logger.info(agent_configurations)

    # Create agent execution in RUNNING state associated with the agent
    execution = AgentExecution(status='RUNNING', agent_id=agent.id, last_execution_time=datetime.utcnow())
    session.add(execution)
    session.commit()

    logger.info("Final Execution")
    logger.info(execution)

    execute_agent.delay(execution.id, datetime.now())


run_superagi_cli(agent_name=agent_name, agent_description=agent_description, agent_goals=agent_goals)
