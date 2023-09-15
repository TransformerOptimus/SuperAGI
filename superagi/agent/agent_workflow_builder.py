import queue

from superagi.agent.agent_workflow_validator import AgentWorkflowValidator
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep


class AgentWorkflowBuilder:
    """AgentWorkflowBuilder class is responsible for building agent workflows from .yaml based workflows."""

    def __init__(self, session, agent_workflow):
        self.session = session
        self.agent_workflow = agent_workflow

    def build_workflow_from_yaml(self, workflow_yaml):
        """Build agent workflow from .yaml file content.

        Args:
            workflow_yaml (str): The workflow content in .yaml format.

        Returns:
            AgentWorkflow: The agent workflow.
        """
        agent_workflow = self.parse_workflow_yaml(workflow_yaml)

        AgentWorkflowValidator(self.session).validate_workflow_steps(agent_workflow)

        trigger_step = self.find_trigger_step(agent_workflow)
        if trigger_step is None:
            raise Exception("Trigger step not found in workflow")
        step_queue = queue.Queue()
        step_queue.put(trigger_step)

        # agent_workflow = AgentWorkflow.create_agent_workflow(self.session, self.agent_id, agent_workflow)
        while not step_queue.empty():
            current_step = step_queue.get()
            print(f"Processing step: {current_step['name']}")

            next_steps = current_step.get("next")
            if next_steps:
                for next_step_info in next_steps:
                    next_step_name = next_step_info.get("step")
                    next_step = self.get_step_by_name(agent_workflow, next_step_name)
                    if next_step:
                        step_queue.put(next_step)

    def parse_workflow_yaml(self, workflow_yaml):
        """Parse the workflow yaml content.

        Args:
            workflow_yaml (str): The workflow content in .yaml format.

        Returns:
            dict: The parsed workflow yaml content.
        """

        workflow = []

        for step_data in workflow_yaml:
            step = {
                "name": step_data["name"],
                "type": step_data["type"]
            }

            if "trigger_step" in step_data:
                step["trigger_step"] = step_data["trigger_step"]

            if "tool" in step_data:
                step["tool"] = step_data["tool"]
                step["instruction"] = step_data["instruction"]

            if "next" in step_data:
                next_steps = []

                if "next_step" in step_data["next"]:
                    next_steps.append({"output": "next_step", "step": step_data["next"]["next_step"]})

                if "exit_step" in step_data["next"]:
                    next_steps.append({"output": "exit_step", "step": step_data["next"]["exit_step"]})

                step["next"] = next_steps

            workflow.append(step)

        return workflow

    def find_trigger_step(self, workflow):
        """Find the trigger step in the workflow."""
        for step in workflow:
            if step["trigger_step"] and step["trigger_step"] == True:
                return step
        return None

    def get_step_by_name(self, workflow, step_name):
        """Get the next step for the given step name."""
        for step in workflow:
            if step["name"] == step_name:
                return step
        return None

    def build_step(self, step):
        """Build agent workflow step."""
       #TODO: Add support for iteration workflow step, conditional workflow step
        if step["type"] == "TOOL":
            return AgentWorkflowStep.find_or_create_tool_workflow_step(session=self.session,
                                                                       agent_workflow_id=self.agent_workflow.id,
                                                                       unique_id=str(self.agent_workflow.id) + "_" +
                                                                                 step["name"],
                                                                       tool_name=step["tool"],
                                                                       input_instruction=step["instruction"])
        elif step["type"] == "LOOP":
            return AgentWorkflowStep.find_or_create_tool_workflow_step(session=self.session,
                                                                       agent_workflow_id=self.agent_workflow.id,
                                                                       unique_id=str(self.agent_workflow.id) + "_" +
                                                                                 step["name"],
                                                                       tool_name="TASK_QUEUE",
                                                                       input_instruction="Break the above response array of items",
                                                                       completion_prompt="Get array of items from the above response. Array should suitable utilization of JSON.parse().")
        elif step["type"] == "WAIT_FOR_PERMISSION":
            return AgentWorkflowStep.find_or_create_tool_workflow_step(session=self.session,
                                                                        agent_workflow_id=self.agent_workflow.id,
                                                                        unique_id=str(self.agent_workflow.id) + "_" +
                                                                                     step["name"],
                                                                        tool_name="WAIT_FOR_PERMISSION",
                                                                        input_instruction=step["instruction"])
        elif step["type"] == "WAIT":
            return AgentWorkflowStep.find_or_create_wait_workflow_step(session=self.session,
                                                                       agent_workflow_id=self.agent_workflow.id,
                                                                       unique_id=str(self.agent_workflow.id) + "_" +
                                                                                 step["name"],
                                                                       delay=step["duration"],
                                                                       wait_description=step["instruction"])