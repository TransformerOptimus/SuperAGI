from fastapi import HTTPException

from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit


class AgentWorkflowValidator:
    """AgentWorkflowValidator class is responsible for validating the yaml workflow of the agent"""

    def __init__(self, session, organisation_id):
        self.session = session
        self.organisation_id = organisation_id
        # self.agent_id = agent_id
        # self.agent_execution_id = agent_execution_id


    def validate_workflow_steps(self, workflow_steps):
        """Validate the workflow steps.

        Returns:
            bool: True if the workflow steps are valid, False otherwise.
        """
        # TODO: validate the workflow steps to be called recursively and check if the step type is one of the valid types
        #  i.e.  LOOP, CONDITION, WAIT, WAIT_FOR_PERMISSION, TOOL, ITERATION_WORKFLOW
        self.validate_unique_step_name(workflow_steps)

        valid_step_types = ["LOOP", "CONDITION", "WAIT", "WAIT_FOR_PERMISSION", "TOOL", "ITERATION_WORKFLOW"]
        for step in workflow_steps["steps"]:
            if step.get("type") not in valid_step_types:
                raise HTTPException(status_code=500, detail=f"Type does not exist in {step}.")

            if step.get("trigger_step") and str(step.get("trigger_step")).upper() == "TRUE":
                self.__validate_trigger_step(step)

            if step.get("type") == "TOOL":
                self.__validata_tool_step(step)
            elif step.get("type") == "LOOP":
                self.__validate_loop_step(step)
            elif step.get("type") == "CONDITION":
                self.__validate_condition_step(step)
            elif step.get("type") == "WAIT":
                self.__validate_wait_step(step)
            elif step.get("type") == "WAIT_FOR_PERMISSION":
                self.__validate_wait_for_permission_step(step)
            elif step.get("type") == "ITERATION_WORKFLOW":
                self.__validate_iteration_workflow_step(step)

    def __validata_tool_step(self, step):
        """Validate the tool step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the tool step is valid, False otherwise.
        """
        if step.get("tool") is None:
            raise HTTPException(status_code=500, detail=f"Tool name not found in step: {step.get('name')}")

        self.__validate_tool(step)

        if step.get("instruction") is None:
            raise HTTPException(status_code=500, detail=f"Instruction not found in step: {step.get('name')}")

        if step.get("next") is None:
            raise HTTPException(status_code=500, detail=f"Next step not found in step: {step.get('name')}")


    def __validate_loop_step(self, step):
        """Validate the loop step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the loop step is valid, False otherwise.
        """
        if step.get("next") is None:
            raise HTTPException(status_code=500, detail=f"Next step not found in step: {step.get('name')}")

        if step.get("next").get("next_step") is None:
            raise HTTPException(status_code=500, detail=f"Next step not found in step: {step.get('name')}")


    def __validate_condition_step(self, step):
        """Validate the condition step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the condition step is valid, False otherwise.
        """
        if step.get("next") is None:
            raise HTTPException(status_code=500, detail=f"Next step not found in step: {step.get('name')}")

        for next_steps in step.get("next"):
            if next_steps.get("step") is None:
                raise HTTPException(status_code=500, detail=f"Next step not found in step: {step.get('name')}")

    def __validate_wait_step(self, step):
        """Validate the wait step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the wait step is valid, False otherwise.
        """
        if step.get("duration") is None:
            raise HTTPException(status_code=500, detail=f"Duration not found in step: {step.get('name')}")

    def __validate_wait_for_permission_step(self, step):
        """Validate the wait for permission step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the wait step is valid, False otherwise.
        """
        if step.get("next") is None:
            raise HTTPException(status_code=500, detail=f"Next step not found in step: {step.get('name')}")

        for next_steps in step.get("next"):
            if next_steps.get("step") is None:
                raise HTTPException(status_code=500, detail=f"Next step not found in step: {step.get('name')}")

            if next_steps.get("output") != "YES" or next_steps.get("output") != "NO":
                raise HTTPException(status_code=500, detail=f"Output can only be Yes/No in step: {step.get('name')}")

    def __validate_iteration_workflow_step(self, step):
        """Validate the iteration workflow step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the iteration workflow step is valid, False otherwise.
        """
        pass

    def __validate_trigger_step(self, step):
        """Validate the trigger step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the trigger step is valid, False otherwise.
        """
        if step.get("type") is None:
            raise HTTPException(status_code=500,detail=f"Type not found in step: {step.get('name')}")

        valid_step_types = ["TOOL", "ITERATION_WORKFLOW", "LOOP"]
        if step.get("type") not in valid_step_types:
            raise HTTPException(status_code=500,detail=f"Type field can only be of type: `TOOL`, "
                                                       f"`ITERATION_WORKFLOW` or `LOOP` in step: {step.get('name')}")


    def validate_unique_step_name(self, workflow_steps):
        """Validate the workflow steps to have unique step names."""

        step_names = set()
        duplicate_names = []
        for step in workflow_steps["steps"]:
            name = step.get("name")
            if name:
                if name in step_names:
                    duplicate_names.append(name)
                else:
                    step_names.add(name)
        if duplicate_names:
            raise HTTPException(status_code=500,detail=f"Duplicate step names found: {duplicate_names}")


    def __validate_tool(self, step):
        """Validate the tool.

        Args:
            tool (Tool): The tool.

        Returns:
            bool: True if the tool is valid, False otherwise.
        """
        toolkit = self.session.query(Tool).filter(Tool.name == step.get("tool")).first()

        if toolkit is None:
            raise HTTPException(status_code=500, detail=f"Invalid tool name in step: {step.get('name')}")

        if not self.session.query(Toolkit).filter(Toolkit.id == toolkit.id,
                                                  Toolkit.organisation_id == self.organisation_id):
            raise HTTPException(status_code=500,detail=f"Tool not installed: {step.get('tool')}")
