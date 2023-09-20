from abc import ABC, abstractmethod

from superagi.agent.types.agent_execution_status import AgentExecutionStatus
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution


class WorkflowStep(ABC):
    def __init__(self, session, llm, agent_execution_id, agent_id, memory):
        self.session = session
        self.llm = llm
        self.agent_execution_id = agent_execution_id
        self.agent_id = agent_id
        self.memory = memory
        # self.task_queue = TaskQueue(str(self.agent_execution_id))
        self.organisation = Agent.find_org_by_agent_id(self.session, self.agent_id)

    @abstractmethod
    def execute(self):
        """
        This method should be implemented by concrete subclasses to define the execution logic for each step.
        """
        pass

    @abstractmethod
    def _handle_next_step(self, next_step):
        if str(next_step) == "COMPLETE":
            agent_execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
            agent_execution.current_agent_step_id = -1
            agent_execution.status = AgentExecutionStatus.COMPLETED.value
        else:
            AgentExecution.assign_next_step_id(self.session, self.agent_execution_id, next_step.id)
        self.session.commit()

