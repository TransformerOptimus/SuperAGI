class AgentWorkflowValidator:
    """AgentWorkflowValidator class is responsible for validating the yaml workflow of the agent"""

    def __init__(self, session):
        self.session = session
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
        for step in workflow_steps:
            if step["type"] not in valid_step_types:
                return False
            if step["type"] == "TOOL":
                if not self.__validata_tool_step(step):
                    return False
            elif step["type"] == "LOOP":
                if not self.__validate_loop_step(step):
                    return False
            elif step["type"] == "CONDITION":
                if not self.__validate_condition_step(step):
                    return False
            elif step["type"] == "WAIT":
                if not self.__validate_wait_step(step):
                    return False
            elif step["type"] == "ITERATION_WORKFLOW":
                if not self.__validate_iteration_workflow_step(step):
                    return False
            return True

    def validate_workflow(self, workflow):
        """Validate the workflow.

        Args:
            workflow (AgentWorkflow): The agent workflow.

        Returns:
            bool: True if the workflow is valid, False otherwise.
        """

        return True

    def __validata_tool_step(self, step):
        """Validate the tool step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the tool step is valid, False otherwise.
        """

        return True

    def __validate_loop_step(self, step):
        """Validate the loop step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the loop step is valid, False otherwise.
        """

        return True

    def __validate_condition_step(self, step):
        """Validate the condition step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the condition step is valid, False otherwise.
        """

        return True

    def __validate_wait_step(self, step):
        """Validate the wait step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the wait step is valid, False otherwise.
        """

        return True

    def __validate_iteration_workflow_step(self, step):
        """Validate the iteration workflow step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the iteration workflow step is valid, False otherwise.
        """

        return True

    def __validate_trigger_step(self, step):
        """Validate the trigger step.

        Args:
            step (dict): The step.

        Returns:
            bool: True if the trigger step is valid, False otherwise.
        """

        return True

    # def __validate_terminal_step(self, step):
    #     """Validate the terminal step.
    #
    #     Args:
    #         step (dict): The step.
    #
    #     Returns:
    #         bool: True if the terminal step is valid, False otherwise.
    #     """
    #
    #     return True

    def validate_unique_step_name(self, workflow_steps):
        """Validate the workflow steps to have unique step names."""

        step_names = set()
        duplicate_names = []

        for step in workflow_steps:
            name = step.get("name")
            if name:
                if name in step_names:
                    duplicate_names.append(name)
                else:
                    step_names.add(name)
        if duplicate_names:
            raise Exception(f"Duplicate step names found: {duplicate_names}")


    def validate_tool(self, tool):
        """Validate the tool.

        Args:
            tool (Tool): The tool.

        Returns:
            bool: True if the tool is valid, False otherwise.
        """

        return True