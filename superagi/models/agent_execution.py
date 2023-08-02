import json
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from superagi.models.base_model import DBBaseModel


class AgentExecution(DBBaseModel):
    """
    Represents single agent run

    Attributes:
        id (int): The unique identifier of the agent execution.
        status (str): The status of the agent execution. Possible values: 'CREATED', 'RUNNING', 'PAUSED',
            'COMPLETED', 'TERMINATED'.
        name (str): The name of the agent execution.
        agent_id (int): The identifier of the associated agent.
        last_execution_time (datetime): The timestamp of the last execution time.
        num_of_calls (int): The number of calls made during the execution.
        num_of_tokens (int): The number of tokens used during the execution.
        current_step_id (int): The identifier of the current step in the execution.
    """

    __tablename__ = 'agent_executions'

    id = Column(Integer, primary_key=True)
    status = Column(String)  # like ('CREATED', 'RUNNING', 'PAUSED', 'COMPLETED', 'TERMINATED')
    name = Column(String)
    agent_id = Column(Integer)
    last_execution_time = Column(DateTime)
    num_of_calls = Column(Integer, default=0)
    num_of_tokens = Column(Integer, default=0)
    current_step_id = Column(Integer)
    permission_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the AgentExecution object.

        Returns:
            str: String representation of the AgentExecution.
        """

        return (
            f"AgentExecution(id={self.id}, name={self.name}, status='{self.status}', "
            f"last_execution_time='{self.last_execution_time}', current_step_id={self.current_step_id}, "
            f"agent_id={self.agent_id}, num_of_calls={self.num_of_calls})"
        )

    def to_dict(self):
        """
        Converts the AgentExecution object to a dictionary.

        Returns:
            dict: Dictionary representation of the AgentExecution.
        """

        return {
            'id': self.id,
            'status': self.status,
            'name': self.name,
            'agent_id': self.agent_id,
            'last_execution_time': self.last_execution_time.isoformat(),
            'num_of_calls': self.num_of_calls,
            'num_of_tokens': self.num_of_tokens,
            'current_step_id': self.current_step_id,
        }

    def to_json(self):
        """
        Converts the AgentExecution object to a JSON string.

        Returns:
            str: JSON string representation of the AgentExecution.
        """

        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        """
        Creates an AgentExecution object from a JSON string.

        Args:
            json_data (str): JSON string representing the AgentExecution object.

        Returns:
            AgentExecution: The created AgentExecution object.
        """

        data = json.loads(json_data)
        last_execution_time = datetime.fromisoformat(data['last_execution_time'])
        return cls(
            id=data['id'],
            status=data['status'],
            name=data['name'],
            agent_id=data['agent_id'],
            last_execution_time=last_execution_time,
            num_of_calls=data['num_of_calls'],
            num_of_tokens=data['num_of_tokens'],
            current_step_id=data['current_step_id'],
        )

    @classmethod
    def get_agent_execution_from_id(cls, session, agent_execution_id):
        """
            Get Agent from agent_id

            Args:
                session: The database session.
                agent_execution_id(int) : Unique identifier of an Agent Execution.

            Returns:
                AgentExecution: AgentExecution object is returned.
        """
        return session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
