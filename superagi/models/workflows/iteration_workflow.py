import json

from sqlalchemy import Column, Integer, String, Text, Boolean

from superagi.models.base_model import DBBaseModel
from superagi.models.workflows.iteration_workflow_step import IterationWorkflowStep


class IterationWorkflow(DBBaseModel):
    """
    Agent workflows which runs part of each agent execution step

    Attributes:
        id (int): The unique identifier of the agent workflow.
        name (str): The name of the agent workflow.
        description (str): The description of the agent workflow.
    """

    __tablename__ = 'iteration_workflows'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    has_task_queue = Column(Boolean, default=False)

    def __repr__(self):
        """
        Returns a string representation of the AgentWorkflow object.

        Returns:
            str: String representation of the AgentWorkflow.
        """

        return f"AgentWorkflow(id={self.id}, name='{self.name}', " \
               f"description='{self.description}')"

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
        Fetches the trigger step ID of the specified iteration workflow.

        Args:
            session: The session object used for database operations.
            workflow_id (int): The ID of the agent workflow.

        Returns:
            int: The ID of the trigger step.

        """

        trigger_step = session.query(IterationWorkflowStep).filter(
            IterationWorkflowStep.iteration_workflow_id == workflow_id,
            IterationWorkflowStep.step_type == 'TRIGGER').first()
        return trigger_step

    @classmethod
    def find_workflow_by_name(cls, session, name: str):
        """
        Finds an IterationWorkflow by name.

        Args:
            session (Session): SQLAlchemy session object.
            name (str): Name of the AgentWorkflow.

        Returns:
            AgentWorkflow: AgentWorkflow object with the given name.
        """
        return session.query(IterationWorkflow).filter(IterationWorkflow.name == name).first()

    @classmethod
    def find_or_create_by_name(cls, session, name: str, description: str, has_task_queue: bool = False):
        """
        Finds an IterationWorkflow by name or creates it if it does not exist.
        Args:
            session (Session): SQLAlchemy session object.
            name (str): Name of the AgentWorkflow.
            description (str): Description of the AgentWorkflow.
        """
        iteration_workflow = session.query(IterationWorkflow).filter(
            IterationWorkflow.name == name).first()
        if iteration_workflow is None:
            iteration_workflow = IterationWorkflow(name=name, description=description)
            session.add(iteration_workflow)
            session.commit()
        iteration_workflow.has_task_queue = has_task_queue
        session.commit()

        return iteration_workflow

    @classmethod
    def find_by_id(cls, session, id: int):
        """ Find the workflow step by id"""
        return session.query(IterationWorkflow).filter(IterationWorkflow.id == id).first()