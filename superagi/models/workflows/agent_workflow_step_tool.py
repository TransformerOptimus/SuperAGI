import json

from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from superagi.models.base_model import DBBaseModel


class AgentWorkflowStepTool(DBBaseModel):
    """
    Step of an agent workflow

    Attributes:
        id (int): The unique identifier of the agent workflow step
        tool_name (str): Tool name
        input_instruction (str): Input Instruction to the tool
        output_instruction (str): Output Instruction to the tool
        history_enabled: whether history enabled in the step
        completion_prompt: completion prompt in the llm conversations
    """

    __tablename__ = 'agent_workflow_step_tools'

    id = Column(Integer, primary_key=True)
    tool_name = Column(String)
    unique_id = Column(String)
    input_instruction = Column(Text)
    output_instruction = Column(Text)
    history_enabled = Column(Boolean)
    completion_prompt = Column(Text)
    
    def __repr__(self):
        """
        Returns a string representation of the AgentWorkflowStep object.

        Returns:
            str: String representation of the AgentWorkflowStep.
        """

        return f"AgentWorkflowStep(id={self.id}, " \
               f"prompt='{self.tool_name}', agent_id={self.tool_instruction})"
    
    def to_dict(self):
        """
        Converts the AgentWorkflowStep object to a dictionary.

        Returns:
            dict: Dictionary representation of the AgentWorkflowStep.
        """

        return {
            'id': self.id,
            'tool_name': self.tool_name,
            'input_instruction': self.input_instruction,
            'output_instruction': self.output_instruction,
            'history_enabled': self.history_enabled,
            'completion_prompt': self.completion_prompt,
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
            tool_name=data['tool_name'],
            input_instruction=data['input_instruction'],
            output_instruction=data['output_instruction'],
            history_enabled=data['history_enabled'],
            completion_prompt=data['completion_prompt'],
        )

    @classmethod
    def find_by_id(cls, session, step_id: int):
        return session.query(AgentWorkflowStepTool).filter(AgentWorkflowStepTool.id == step_id).first()

    @classmethod
    def find_or_create_tool(cls, session, step_unique_id: str, tool_name: str,
                            input_instruction: str, output_instruction: str,
                            history_enabled: bool = False, completion_prompt: str = None):
        """
        Finds or creates a tool in the database.

        Args:
            session (Session): SQLAlchemy session object.
            step_unique_id (str): Unique ID of the step.
            tool_name (str): Name of the tool.
            input_instruction (str): Tool input instructions.
            output_instruction (str): Tool output instructions.
            history_enabled (bool): Whether history is enabled for the tool.
            completion_prompt (str): Completion prompt for the tool.

        Returns:
            AgentWorkflowStepTool: The AgentWorkflowStepTool object.
        """
        unique_id = f"{step_unique_id}_{tool_name}"
        tool = session.query(AgentWorkflowStepTool).filter_by(
            unique_id=unique_id
        ).first()

        if tool is None:
            tool = AgentWorkflowStepTool(tool_name=tool_name, unique_id=unique_id,
                                         input_instruction=input_instruction,
                                         output_instruction=output_instruction,
                                         history_enabled=history_enabled,
                                         completion_prompt=completion_prompt)
            session.add(tool)
        else:
            tool.tool_name = tool_name
            tool.input_instruction = input_instruction
            tool.output_instruction = output_instruction
            tool.history_enabled = history_enabled
            tool.completion_prompt = completion_prompt
        session.commit()
        return tool

