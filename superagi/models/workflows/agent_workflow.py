import json
from typing import Optional

from sqlalchemy import Column, Integer, String, Text

from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.base_model import DBBaseModel


class AgentWorkflow(DBBaseModel):
    """
    Agent workflows which runs part of each agent execution step

    Attributes:
        id (int): The unique identifier of the agent workflow.
        name (str): The name of the agent workflow.
        description (str): The description of the agent workflow.
    """

    __tablename__ = 'agent_workflows'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    organisation_id = Column(Integer)
    code_yaml = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the AgentWorkflow object.

        Returns:
            str: String representation of the AgentWorkflow.
        """

        return f"AgentWorkflow(id='{self.id}', name='{self.name}', " \
               f"description='{self.description}', " \
               f"organisation id='{self.organisation_id}', "\
               f"workflow code='{self.code_yaml}')"

    def to_dict(self):
        """
            Converts the AgentWorkflow object to a dictionary.

            Returns:
                dict: Dictionary representation of the AgentWorkflow.
        """

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def to_json(self):
        """
        Converts the AgentWorkflow object to a JSON string.

        Returns:
            str: JSON string representation of the AgentWorkflow.
        """

        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        """
        Creates an AgentWorkflow object from a JSON string.

        Args:
            json_data (str): JSON string representing the AgentWorkflow.

        Returns:
            AgentWorkflow: AgentWorkflow object created from the JSON string.
        """

        data = json.loads(json_data)
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description']
        )

    @classmethod
    def fetch_trigger_step_id(cls, session, workflow_id):
        """
        Fetches the trigger step ID of the specified agent workflow.

        Args:
            session: The session object used for database operations.
            workflow_id (int): The ID of the agent workflow.

        Returns:
            int: The ID of the trigger step.

        """
        trigger_step = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.agent_workflow_id == workflow_id,
                                                               AgentWorkflowStep.step_type == 'TRIGGER').first()
        return trigger_step

    @classmethod
    def find_by_id(cls, session, id: int):
        """Create or find an agent workflow by id."""
        return session.query(AgentWorkflow).filter(AgentWorkflow.id == id).first()


    @classmethod
    def find_by_name(cls, session, name: str):
        """Create or find an agent workflow by name."""
        return session.query(AgentWorkflow).filter(AgentWorkflow.name == name).first()

    @classmethod
    def find_or_create_by_name(cls, session, name: str, description: str, organisation_id: Optional[int] = None):
        """Create or find an agent workflow by name."""
        print("Session : ",session)
        print("Name : ",name)
        print("Description : ",description)
        agent_workflow = session.query(AgentWorkflow).filter(AgentWorkflow.name == name).first()
        print("Agent Workflow : ",agent_workflow)
        if agent_workflow is None:
            agent_workflow = AgentWorkflow(name=name, description=description, organisation_id=organisation_id)
            session.add(agent_workflow)
            session.commit()
        return agent_workflow

    @classmethod
    def find_by_organisation_id(cls, session, organisation_id: int):
        workflows = session.query(AgentWorkflow).filter(AgentWorkflow.organisation_id == organisation_id).all()
        return workflows

    @classmethod
    def add_or_update_agent_workflow_code_yaml(cls, session, id: int, agent_workflow_code_yaml: str):
        agent_workflow = session.query(AgentWorkflow).filter(AgentWorkflow.id == id).first()

        if agent_workflow is not None:
            agent_workflow.code_yaml = agent_workflow_code_yaml
            session.commit()

        return agent_workflow

