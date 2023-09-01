from superagi.models.agent_execution import AgentExecution
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_wait import AgentWorkflowStepWait


class AgentWaitStepHandler:
    """Handle Agent Wait Step in the agent workflow."""

    def __init__(self,session, agent_id, agent_execution_id):
        self.session = session
        self.agent_id = agent_id
        self.agent_execution_id = agent_execution_id

    def execute_step(self):
        """Execute the agent wait step."""

        execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
        workflow_step = AgentWorkflowStep.find_by_id(self.session, execution.current_agent_step_id)
        step_wait = AgentWorkflowStepWait.find_by_id(self.session, workflow_step.action_reference_id)
