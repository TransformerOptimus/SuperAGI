from __future__ import annotations

import json

from sqlalchemy import Column, Integer, String

import superagi.models
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_template import AgentTemplate
from superagi.models.agent_template_config import AgentTemplateConfig
from superagi.models.agent_workflow import AgentWorkflow
# from superagi.models import AgentConfiguration
from superagi.models.base_model import DBBaseModel
from superagi.lib.logger import logger
from superagi.models.organisation import Organisation
from superagi.models.project import Project

class Agent(DBBaseModel):
    """
    Represents an agent entity.

    Attributes:
        id (int): The unique identifier of the agent.
        name (str): The name of the agent.
        project_id (int): The identifier of the associated project.
        description (str): The description of the agent.
        agent_workflow_id (int): The identifier of the associated agent workflow.
    """

    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    project_id = Column(Integer)
    description = Column(String)
    agent_workflow_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the Agent object.

        Returns:
            str: String representation of the Agent.

        """
        return f"Agent(id={self.id}, name='{self.name}', project_id={self.project_id}, " \
               f"description='{self.description}', agent_workflow_id={self.agent_workflow_id})"

    @classmethod
    def fetch_configuration(cls, session, agent_id: int):
        """
        Fetches the configuration of an agent.

        Args:
            session: The database session object.
            agent_id (int): The ID of the agent.

        Returns:
            dict: Parsed agent configuration.

        """

        agent = session.query(Agent).filter_by(id=agent_id).first()
        agent_configurations = session.query(superagi.models.agent_config.AgentConfiguration).filter_by(
            agent_id=agent_id).all()
        parsed_config = {
            "agent_id": agent.id,
            "name": agent.name,
            "project_id": agent.project_id,
            "description": agent.description,
            "goal": [],
            "instruction": [],
            "agent_type": None,
            "constraints": [],
            "tools": [],
            "exit": None,
            "iteration_interval": None,
            "model": None,
            "permission_type": None,
            "LTM_DB": None,
            "memory_window": None,
            "max_iterations": None
        }
        if not agent_configurations:
            return parsed_config
        for item in agent_configurations:
            parsed_config[item.key] = cls.eval_agent_config(item.key, item.value)
        return parsed_config

    @classmethod
    def eval_agent_config(cls, key, value):
        """
        Evaluates the value of an agent configuration setting based on its key.

        Args:
            key (str): The key of the configuration setting.
            value (str): The value of the configuration setting.

        Returns:
            object: The evaluated value of the configuration setting.

        """

        if key in ["name", "description", "agent_type", "exit", "model", "permission_type", "LTM_DB", "resource_summary"]:
            return value
        elif key in ["project_id", "memory_window", "max_iterations", "iteration_interval"]:
            return int(value)
        elif key == "goal" or key == "constraints" or key == "instruction":
            return eval(value)
        elif key == "tools":
            return [int(x) for x in json.loads(value)]

    @classmethod
    def create_agent_with_config(cls, db, agent_with_config):
        """
        Creates a new agent with the provided configuration.

        Args:
            db: The database object.
            agent_with_config: The object containing the agent and configuration details.

        Returns:
            Agent: The created agent.

        """

        db_agent = Agent(name=agent_with_config.name, description=agent_with_config.description,
                         project_id=agent_with_config.project_id)
        db.session.add(db_agent)
        db.session.flush()  # Flush pending changes to generate the agent's ID
        db.session.commit()

        if agent_with_config.agent_type == "Don't Maintain Task Queue":
            agent_workflow = db.session.query(AgentWorkflow).filter(AgentWorkflow.name == "Goal Based Agent").first()
            logger.info(agent_workflow)
            db_agent.agent_workflow_id = agent_workflow.id
        elif agent_with_config.agent_type == "Maintain Task Queue":
            agent_workflow = db.session.query(AgentWorkflow).filter(
                AgentWorkflow.name == "Task Queue Agent With Seed").first()
            db_agent.agent_workflow_id = agent_workflow.id
        elif agent_with_config.agent_type == "Fixed Task Queue":
            agent_workflow = db.session.query(AgentWorkflow).filter(
                AgentWorkflow.name == "Fixed Task Queue").first()
            db_agent.agent_workflow_id = agent_workflow.id


        db.session.commit()

        # Create Agent Configuration
        agent_config_values = {
            "goal": agent_with_config.goal,
            "instruction": agent_with_config.instruction,
            "agent_type": agent_with_config.agent_type,
            "constraints": agent_with_config.constraints,
            "tools": agent_with_config.tools,
            "exit": agent_with_config.exit,
            "iteration_interval": agent_with_config.iteration_interval,
            "model": agent_with_config.model,
            "permission_type": agent_with_config.permission_type,
            "LTM_DB": agent_with_config.LTM_DB,
            "max_iterations": agent_with_config.max_iterations,
            "user_timezone": agent_with_config.user_timezone
        }

        agent_configurations = [
            AgentConfiguration(agent_id=db_agent.id, key=key, value=str(value))
            for key, value in agent_config_values.items()
        ]

        db.session.add_all(agent_configurations)
        db.session.commit()
        db.session.flush()
        return db_agent

    @classmethod
    def create_agent_with_template_id(cls, db, project_id, agent_template):
        """
        Creates a new agent using the provided agent template ID.

        Args:
            db: The database object.
            project_id (int): The ID of the project.
            agent_template: The agent template object.

        Returns:
            Agent: The created agent.

        """

        db_agent = Agent(name=agent_template.name, description=agent_template.description,
                         project_id=project_id,
                         agent_workflow_id=agent_template.agent_workflow_id)
        db.session.add(db_agent)
        db.session.flush()  # Flush pending changes to generate the agent's ID
        db.session.commit()

        configs = db.session.query(AgentTemplateConfig).filter(
            AgentTemplateConfig.agent_template_id == agent_template.id).all()

        agent_configurations = []
        for config in configs:
            agent_configurations.append(AgentConfiguration(agent_id=db_agent.id, key=config.key, value=config.value))
        db.session.add_all(agent_configurations)
        db.session.commit()
        db.session.flush()
        return db_agent

    @classmethod
    def create_agent_with_marketplace_template_id(cls, db, project_id, agent_template_id):
        """
        Creates a new agent using the agent template ID from the marketplace.

        Args:
            db: The database object.
            project_id (int): The ID of the project.
            agent_template_id (int): The ID of the agent template from the marketplace.

        Returns:
            Agent: The created agent.

        """

        agent_template = AgentTemplate.fetch_marketplace_detail(agent_template_id)
        # we need to create agent workflow if not present. Add it once we get org id in agent workflow
        db_agent = Agent(name=agent_template["name"], description=agent_template["description"],
                         project_id=project_id,
                         agent_workflow_id=agent_template["agent_workflow_id"])
        db.session.add(db_agent)
        db.session.flush()  # Flush pending changes to generate the agent's ID
        db.session.commit()

        agent_configurations = []
        for key, value in agent_template["configs"].items():
            agent_configurations.append(AgentConfiguration(agent_id=db_agent.id, key=key, value=value["value"]))
        db.session.add_all(agent_configurations)
        db.session.commit()
        db.session.flush()
        return db_agent

    def get_agent_organisation(self, session):
        """
        Get the organization of the agent.

        Args:
            session: The database session.

        Returns:
            Organization: The organization of the agent.

        """
        project = session.query(Project).filter(Project.id == self.project_id).first()
        return session.query(Organisation).filter(Organisation.id == project.organisation_id).first()

    @classmethod
    def get_agent_from_id(cls, session, agent_id):
        """
            Get Agent from agent_id

            Args:
                session: The database session.
                agent_id(int) : Unique identifier of an Agent.

            Returns:
                Agent: Agent object is returned.
        """
        return session.query(Agent).filter(Agent.id == agent_id).first()
