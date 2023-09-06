from datetime import datetime

from superagi.agent.types.agent_execution_status import AgentExecutionStatus
from superagi.lib.logger import logger
from superagi.models.agent_execution import AgentExecution
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_wait import AgentWorkflowStepWait
from superagi.agent.types.wait_step_status import AgentWorkflowStepWaitStatus

class AgentWaitStepHandler:
    """Handle Agent Wait Step in the agent workflow."""

    def __init__(self, session, agent_id, agent_execution_id):
        self.session = session
        self.agent_id = agent_id
        self.agent_execution_id = agent_execution_id

    def execute_step(self):
        """Execute the agent wait step."""

        logger.info("Executing Wait Step")
        execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
        workflow_step = AgentWorkflowStep.find_by_id(self.session, execution.current_agent_step_id)
        step_wait = AgentWorkflowStepWait.find_by_id(self.session, workflow_step.action_reference_id)
        if step_wait is not None:
            step_wait.wait_begin_time = datetime.now()
            step_wait.status = AgentWorkflowStepWaitStatus.WAITING.value
            execution.status = AgentExecutionStatus.WAIT_STEP.value

            self.session.commit()

    def handle_next_step(self):
        """Handle next step of agent workflow in case of wait step."""

        execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
        workflow_step = AgentWorkflowStep.find_by_id(self.session, execution.current_agent_step_id)
        step_response = "default"
        next_step = AgentWorkflowStep.fetch_next_step(self.session, workflow_step.id, step_response)
        if str(next_step) == "COMPLETE":
            agent_execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
            agent_execution.current_agent_step_id = -1
            agent_execution.status = "COMPLETED"
        else:
            AgentExecution.assign_next_step_id(self.session, self.agent_execution_id, next_step.id)
        self.session.commit()
