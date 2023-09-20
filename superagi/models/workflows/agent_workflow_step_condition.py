from sqlalchemy import Column, Integer, String, DateTime
import json  # for JSON serialization

from superagi.models.base_model import DBBaseModel


class AgentWorkflowStepCondition(DBBaseModel):
    """
    Step for an Agent Workflow condition.

    Attributes:
        id (int): The unique identifier of the condition step.
        instruction (str): The instruction or condition description.
        tool_output (str): The output from a tool or condition evaluation result.
    """

    __tablename__ = 'agent_workflow_step_conditions'

    id = Column(Integer, primary_key=True)
    instruction = Column(String)
    tool_output = Column(String)
    tool_name = Column(String)
    unique_id = Column(String)

    # status = Column(String)  # 'PENDING', 'EVALUATED', 'COMPLETED'

    def __repr__(self):
        """
        Returns a string representation of the AgentWorkflowStepCondition object.

        Returns:
            str: String representation of the AgentWorkflowStepCondition.
        """

        return f"AgentWorkflowStepCondition(id={self.id}, instruction='{self.instruction}', " \
               f"tool_output='{self.tool_output}', unique_id='{self.unique_id}, tool_name='{self.tool_name}')"

    def to_dict(self):
        """
        Converts the AgentWorkflowStepCondition object to a dictionary.

        Returns:
            dict: Dictionary representation of the AgentWorkflowStepCondition.
        """

        return {
            'id': self.id,
            'instruction': self.instruction,
            'tool_output': self.tool_output,
            'unique_id': self.unique_id,
            'tool_name': self.tool_name,
        }

    def to_json(self):
        """
        Converts the AgentWorkflowStepCondition object to a JSON string.

        Returns:
            str: JSON string representation of the AgentWorkflowStepCondition.
        """

        return json.dumps(self.to_dict())

    @classmethod
    def find_or_create(cls, session, step_unique_id: str, instruction: str):
        """
        Find or create an AgentWorkflowStepCondition.

        Args:
            session (Session): The database session.
            step_unique_id (str): The unique ID of the step.
            instruction (str): The instruction or condition description.

        Returns:
            AgentWorkflowStepCondition: The AgentWorkflowStepCondition.
        """

        unique_id = f"{step_unique_id}_condition"
        print("unique : ",unique_id)
        condition_step = session.query(AgentWorkflowStepCondition).filter(
            AgentWorkflowStepCondition.unique_id == unique_id).first()

        print('condition_step : ',condition_step)
        if condition_step is None:
            condition_step = AgentWorkflowStepCondition(
                unique_id=unique_id,
                instruction=instruction,
            )
            session.add(condition_step)
        else:
            condition_step.instruction = instruction
        session.commit()
        session.flush()
        return condition_step

    @classmethod
    def update_tool_info(cls, session, step_unique_id: str, tool_output: str, tool_name: str):
        """
        Update the tool output of an AgentWorkflowStepCondition.

        Args:
            session (Session): The database session.
            step_unique_id (str): The unique ID of the step.
            tool_output (str): The tool output.
            tool_name (str): The tool name.

        Returns:
            AgentWorkflowStepCondition: The AgentWorkflowStepCondition.
        """

        unique_id = f"{step_unique_id}_condition"
        condition_step = session.query(AgentWorkflowStepCondition).filter(
            AgentWorkflowStepCondition.unique_id == unique_id).first()
        if condition_step is None:
            raise ValueError(f"Condition step with unique ID {unique_id} not found.")
        condition_step.tool_output = tool_output
        condition_step.tool_name = tool_name
        session.commit()
        session.flush()
        return condition_step

    @classmethod
    def find_by_id(cls, session, step_id: int):
        """
        Find an AgentWorkflowStepCondition by ID.

        Args:
            session (Session): The database session.
            step_id (int): The ID of the step.

        Returns:
            AgentWorkflowStepCondition: The AgentWorkflowStepCondition.
        """

        return session.query(AgentWorkflowStepCondition).filter(AgentWorkflowStepCondition.id == step_id).first()
