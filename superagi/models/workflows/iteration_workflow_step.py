import json

from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from superagi.models.base_model import DBBaseModel


class IterationWorkflowStep(DBBaseModel):
    """
    Step of an iteration workflow

    Attributes:
        id (int): The unique identifier of the agent workflow step.
        iteration_workflow_id (int): The ID of the agent workflow to which this step belongs.
        unique_id (str): The unique identifier of the step.
        prompt (str): The prompt for the step.
        variables (str): The variables associated with the step.
        output_type (str): The output type of the step.
        step_type (str): The type of the step (TRIGGER, NORMAL).
        next_step_id (int): The ID of the next step in the workflow.
        history_enabled (bool): Indicates whether history is enabled for the step.
        completion_prompt (str): The completion prompt for the step.
    """

    __tablename__ = 'iteration_workflow_steps'

    id = Column(Integer, primary_key=True)
    iteration_workflow_id = Column(Integer)
    unique_id = Column(String)
    prompt = Column(Text)
    variables = Column(Text)
    output_type = Column(String)
    step_type = Column(String)  # TRIGGER, NORMAL
    next_step_id = Column(Integer)
    history_enabled = Column(Boolean)
    completion_prompt = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the AgentWorkflowStep object.

        Returns:
            str: String representation of the AgentWorkflowStep.
        """

        return f"AgentWorkflowStep(id={self.id}, status='{self.next_step_id}', " \
               f"prompt='{self.prompt}', agent_id={self.agent_id})"
    
    def to_dict(self):
        """
        Converts the AgentWorkflowStep object to a dictionary.

        Returns:
            dict: Dictionary representation of the AgentWorkflowStep.
        """

        return {
            'id': self.id,
            'next_step_id': self.next_step_id,
            'agent_id': self.agent_id,
            'prompt': self.prompt
        }

    def to_json(self):
        """
        Converts the AgentWorkflowStep object to a JSON string.

        Returns:
            str: JSON string representation of the AgentWorkflowStep.
        """

        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        """
        Creates an AgentWorkflowStep object from a JSON string.

        Args:
            json_data (str): JSON string representing the AgentWorkflowStep.

        Returns:
            AgentWorkflowStep: AgentWorkflowStep object created from the JSON string.
        """

        data = json.loads(json_data)
        return cls(
            id=data['id'],
            prompt=data['prompt'],
            agent_id=data['agent_id'],
            next_step_id=data['next_step_id']
        )

    @classmethod
    def find_by_id(cls, session, step_id: int):
        return session.query(IterationWorkflowStep).filter(IterationWorkflowStep.id == step_id).first()

    @classmethod
    def find_or_create_step(self, session, iteration_workflow_id: int, unique_id: str,
                            prompt: str, variables: str, step_type: str, output_type: str,
                            completion_prompt: str = "", history_enabled: bool = False):
        workflow_step = session.query(IterationWorkflowStep).filter(IterationWorkflowStep.unique_id == unique_id).first()
        if workflow_step is None:
            workflow_step = IterationWorkflowStep(unique_id=unique_id)
            session.add(workflow_step)
            session.commit()

        workflow_step.prompt = prompt
        workflow_step.variables = variables
        workflow_step.step_type = step_type
        workflow_step.output_type = output_type
        workflow_step.iteration_workflow_id = iteration_workflow_id
        workflow_step.next_step_id = -1
        workflow_step.history_enabled = history_enabled
        if completion_prompt:
            workflow_step.completion_prompt = completion_prompt
        session.commit()
        return workflow_step



