import json

from sqlalchemy import Column, Integer, String, DateTime

from superagi.models.base_model import DBBaseModel


class AgentWorkflowStepWait(DBBaseModel):
    """
    Step for a Agent Workflow to wait

    Attributes:
        id (int): The unique identifier of the wait block step.
        name (str): The name of the wait block step.
        description (str): The description of the wait block step.
        delay (int): The delay time in seconds.
        wait_begin_time (DateTime): The start time of the wait block.
    """

    __tablename__ = 'agent_workflow_step_waits'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    unique_id = Column(String)
    delay = Column(Integer)  # Delay is stored in seconds
    wait_begin_time = Column(DateTime)
    status = Column(String)  # 'PENDING', 'WAITING', 'COMPLETED'

    def __repr__(self):
        """
        Returns a string representation of the WaitBlockStep object.

        Returns:
            str: String representation of the WaitBlockStep.
        """

        return f"WaitBlockStep(id={self.id}, name='{self.name}', delay='{self.delay}', " \
               f"wait_begin_time='{self.wait_begin_time}'"

    def to_dict(self):
        """
        Converts the WaitBlockStep object to a dictionary.

        Returns:
            dict: Dictionary representation of the WaitBlockStep.
        """

        return {
            'id': self.id,
            'name': self.name,
            'delay': self.delay,
            'wait_begin_time': self.wait_begin_time
        }

    def to_json(self):
        """
        Converts the WaitBlockStep object to a JSON string.

        Returns:
            str: JSON string representation of the WaitBlockStep.
        """

        return json.dumps(self.to_dict())

    @classmethod
    def find_by_id(cls, session, step_id: int):
        return session.query(AgentWorkflowStepWait).filter(AgentWorkflowStepWait.id == step_id).first()

    @classmethod
    def find_or_create_wait(cls, session, step_unique_id: str, description: str, delay: int):
        unique_id = f"{step_unique_id}_wait"
        wait = session.query(AgentWorkflowStepWait).filter(AgentWorkflowStepWait.unique_id == unique_id).first()
        if wait is None:
            wait = AgentWorkflowStepWait(
                unique_id=unique_id,
                name=unique_id,
                delay=delay,
                description=description,
                status='PENDING'
            )
            session.add(wait)
        else:
            wait.delay = delay
            wait.description = description
            wait.status = 'PENDING'
        session.commit()
        session.flush()
        return wait
