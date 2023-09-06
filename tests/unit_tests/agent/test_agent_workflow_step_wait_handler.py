import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from superagi.agent.agent_workflow_step_wait_handler import AgentWaitStepHandler
from superagi.lib.logger import logger
from superagi.models.agent_execution import AgentExecution
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_wait import AgentWorkflowStepWait
# from your_module import AgentWaitStepHandler

class TestAgentWaitStepHandler(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock()
        self.agent_id = 1
        self.agent_execution_id = 2
        self.handler = AgentWaitStepHandler(self.session, self.agent_id, self.agent_execution_id)

    def test_execute_step(self):
        # Mock the necessary objects and methods
        agent_execution = MagicMock()
        workflow_step = MagicMock()
        step_wait = MagicMock()

        AgentExecution.get_agent_execution_from_id = MagicMock(return_value=agent_execution)
        AgentWorkflowStep.find_by_id = MagicMock(return_value=workflow_step)
        AgentWorkflowStepWait.find_by_id = MagicMock(return_value=step_wait)

        # Call the method to be tested
        self.handler.execute_step()

        # Assert that the expected methods were called with the expected arguments
        AgentExecution.get_agent_execution_from_id.assert_called_once_with(self.session, self.agent_execution_id)
        AgentWorkflowStep.find_by_id.assert_called_once_with(self.session, agent_execution.current_agent_step_id)
        AgentWorkflowStepWait.find_by_id.assert_called_once_with(self.session, workflow_step.action_reference_id)

        # Assert that the attributes of step_wait were modified as expected with a tolerance of 1 second
        self.assertAlmostEqual(
            step_wait.wait_begin_time,
            datetime.now(),
            delta=timedelta(seconds=1)  # Specify a tolerance of 1 second
        )

        self.assertEqual(step_wait.status, "WAITING")
        self.assertEqual(agent_execution.status, "WAIT_STEP")
        self.session.commit.assert_called_once()

    def test_handle_next_step(self):
        # Mock the necessary objects and methods
        agent_execution = MagicMock()
        workflow_step = MagicMock()

        # Mock the get_agent_execution_from_id method to return the agent_execution
        AgentExecution.get_agent_execution_from_id = MagicMock(return_value=agent_execution)

        # Mock other methods and attributes
        agent_execution.current_agent_step_id = 42  # Set a specific step ID for testing
        AgentWorkflowStep.find_by_id = MagicMock(return_value=workflow_step)
        AgentWorkflowStep.fetch_next_step = MagicMock(return_value="COMPLETE")
        AgentExecution.assign_next_step_id = MagicMock()

        # Call the method to be tested
        self.handler.handle_next_step()

        # Assert that the expected methods were called with the expected arguments
        AgentWorkflowStep.find_by_id.assert_called_once_with(self.session, 42)  # Ensure it's the correct step ID
        AgentWorkflowStep.fetch_next_step.assert_called_once_with(self.session, workflow_step.id, "default")

        # Assert that the attributes of agent_execution were modified as expected
        self.assertEqual(agent_execution.current_agent_step_id, -1)
        self.assertEqual(agent_execution.status, "COMPLETED")
        self.session.commit.assert_called_once()